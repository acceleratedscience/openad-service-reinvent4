#!/usr/bin/env python

from __future__ import annotations
import copy
import csv
import datetime
import getpass
import json
import logging
import numpy as np
import os
import platform
import random
import string
import rdkit
import subprocess as sp
import sys
import tempfile
import torch
from pydantic.v1 import BaseModel, Field
from rdkit import rdBase, RDLogger
from typing import List, Optional, Union, Dict, Any
from validation import ReinventConfig
from reinvent import version, runmodes
# from reinvent.runmodes.reporter.remote import setup_reporter
from reinvent.runmodes.utils import set_torch_device
from reinvent.utils import config_parse, setup_logger, setup_reporter
from openad_service_utils.common.algorithms.core import Predictor
from openad_service_utils import (
    SimplePredictor,
    PredictorTypes, 
    DomainSubmodule, 
    PropertyInfo
)
from runner_templates import *
from openad_service_utils import start_server

INPUT_FORMAT_CHOICES = ("toml", "json")
RDKIT_CHOICES = ("all", "error", "warning", "info", "debug")
LOGLEVEL_CHOICES = tuple(level.lower() for level in logging._nameToLevel.keys())
VERSION_STR = f"{version.__progname__} {version.__version__} {version.__copyright__}"
OVERWRITE_STR = "Overwrites setting in the configuration file"
RESPONDER_TOKEN = "RESPONDER_TOKEN"

#rdBase.DisableLog("rdApp.*")
rdBase.LogToPythonLogger()

class ClassificationModel:
    """Does nothing. example for a torch model"""
    def __init__(self, model_path, tokenizer) -> None:
        pass
    def to(*args, **kwargs):
        pass
    def eval(*args, **kwargs):
        pass

class Reinvent4Predictor(SimplePredictor):
    """ Implementation of SimplePredictor to execute REINVENT4 scoring """

    def get_predictor(self, configuration: AlgorithmConfiguration):
        """overwrite existing function to not download any models"""
        print("no predictor")

    # s3 path: domain / algorithm_name / algorithm_application / algorithm_version
    # necessary params
    domain: DomainSubmodule = DomainSubmodule("molecules")
    algorithm_name: str = "reinvent4algorithm"
    algorithm_application: str = "Reinvent4Predictor"
    algorithm_version: str = "v0"
    property_type = PredictorTypes.MOLECULE 
    available_properties: List[PropertyInfo] = [PropertyInfo(name="alerts", description="Alerts"), PropertyInfo(name="qed", description="Quantitative estimation of drug-likeness"), PropertyInfo(name="pmi", description="Principal Moments of Inertia"), PropertyInfo(name="pmi2", description="Principal Moments of Inertia 2"), PropertyInfo(name="pmi_raw", description="Principal Moments of Inertia RAW"), PropertyInfo(name="pmi2_raw", description="Principal Moments of Inertia 2 RAW"), PropertyInfo(name="tanimoto", description="Tanimoto coefficient"), PropertyInfo(name="mw", description="Molecular Weight"), PropertyInfo(name="qed_raw", description="Quantitative estimation of drug-likeness RAW"), PropertyInfo(name="pmi_raw", description="Principal Moments of Inertia RAW"), PropertyInfo(name="tanimoto_raw", description="Tanimoto coefficient RAW"), PropertyInfo(name="mw_raw", description="Molecular Weight RAW")]
    
    # REINVENT4 Variables for Scoring

    scoring_type: str = Field(default="geometric_mean", description="")
    scoring_parallel: bool = Field(default=False, description="")

    alerts_name: str = Field(default="Alerts", description="")
    alerts_smarts: list = Field(default=[], description="")

    qed_name: str = Field(default="QED", description="")
    qed_weight: float = Field(default=0.25, description="")

    mw_name: str = Field(default="MW", description="")
    mw_weight: str = Field(default=0.25, description="")
    mw_transform_type: str = Field(default="double_sigmoid", description="")
    mw_transform_high: float = Field(default=500.0, description="")
    mw_transform_low: float = Field(default=200.0, description="")
    mw_transform_coef_div: float = Field(default=500.0, description="")
    mw_transform_coef_si: float = Field(default=20.0, description="")
    mw_transform_coef_se: float = Field(default=20.0, description="")

    tanimoto_name: str = Field(default="Tanimoto similarity ECF6", description="")
    tanimoto_weight: float = Field(default=0.1, description="")
    tanimoto_smiles: list = Field(default=["n1(nc(c(c1C)-c2n[nH]c(c2)[C@@]3([C@@H](CN(CC3)Cc4nc5c(c(n4)C)cccc5)O)OC)C)C"], description="")
    tanimoto_radius: int = Field(default=3, description="")
    tanimoto_use_counts: bool = Field(default=True, description="")
    tanimoto_use_features: bool = Field(default=True, description="")

    pmi_name: str = Field(default="PMI 3D-likeness", description="")
    pmi_weight_1: float = Field(default=0.79, description="")
    pmi_property_1: str = Field(default="npr1", description="")
    pmi_weight_2: float = Field(default=0.21, description="")
    pmi_property_2: str = Field(default="npr2", description="")

    def setup(self):
        pass

    def predict(self, sample: Any):
        """ Execute a scoring for a single SMILES string

        :returns: Results of the REINVENT4 runner execution
        """ 

        # Vars used to execute REINVENT4 runner

        dev = "cpu"
        tb = ""
        resp = "" 
        write = ""
 
        def setup_responder(config):
            """Setup for Reinvent4 remote monitor
            :param config: configuration
            """
            endpoint = config.get("endpoint", False)
            if not endpoint:
                return

            token = os.environ.get(RESPONDER_TOKEN, None)
            setup_reporter(endpoint, token)

        def extract_sections(config: dict) -> dict:
            """Extract the sections of a config file
    
            :param config: the config file
            :returns: the extracted sections
            """
            return {k: v for k, v in config.items() if isinstance(v, (dict, list))}
        def get_temp_file(prefix, suffix):
            """Get temp file names for storing CSV and SMILES work files

            :param prefix: Prefix used for temp file name
            :param suffix: Suffix used for temp file name (csv, smi)
            :returns: a temporary file object
            """
            return(tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix=f"{suffix}", prefix=f"{prefix}"))

        def nuke_file(filename):
            """Delete temp files when finished with analyses

            :param filename: Name of file to delete
            """
            try:
                os.remove(filename)
            except OSError as e:
                print(f"Error deleting {filename}: {e}")

        def get_csv_data_column_label(name, prop):
            name += " (raw)" if prop[-4:] == "_raw" else ""
            return name

        file_prefix = "reinvent4_scoring_"
        """score_input_file is the filename of the file with the single SMILES string for analysis"""
        score_input_file = get_temp_file(file_prefix, ".smi")
        with open(score_input_file.name, "w") as file:
            # file.write("SMILES\n")
            file.write(sample)
        score_input_file.seek(0)
        """score_output_file contains raw output from REINVENT4 analysis"""
        score_output_file = get_temp_file(file_prefix, ".csv") 
        scoring_config["parameters"]["smiles_file"] = score_input_file.name
        scoring_config["parameters"]["output_csv"] = score_output_file.name
        """Identify which property to calculate/output """
        match self.selected_property[:2]:
            case "al": # Alerts
                scoring_component = custom_alerts_config
                csv_data_column_label = scoring_component[0]["custom_alerts"]["endpoint"][0]["name"] = self.alerts_name
                double_quote_smarts = json.dumps(self.alerts_smarts)
                dq_alerts_smarts = json.loads(double_quote_smarts)
                scoring_component[0]["custom_alerts"]["endpoint"][0]["params"]["smarts"] = dq_alerts_smarts
            case "qe": # QED
                scoring_component = qed_config
                scoring_component[0]["QED"]["endpoint"][0][0] = self.qed_name
                scoring_component[0]["QED"]["endpoint"][0]["weight"] = self.qed_weight
                csv_data_column_label = get_csv_data_column_label(self.qed_name, self.selected_property)
            case "mw": # Molecular weight
                scoring_component = molecular_weight_config
                scoring_component[0]["MolecularWeight"]["endpoint"][0]["name"] = self.mw_name
                scoring_component[0]["MolecularWeight"]["endpoint"][0]["weight"] = self.mw_weight
                scoring_component[0]["MolecularWeight"]["endpoint"][0]["transform"]["type"] = self.mw_transform_type
                scoring_component[0]["MolecularWeight"]["endpoint"][0]["transform"]["high"] = self.mw_transform_high
                scoring_component[0]["MolecularWeight"]["endpoint"][0]["transform"]["low"] = self.mw_transform_low
                scoring_component[0]["MolecularWeight"]["endpoint"][0]["transform"]["coef_div"] = self.mw_transform_coef_div
                scoring_component[0]["MolecularWeight"]["endpoint"][0]["transform"]["coef_si"] = self.mw_transform_coef_si
                scoring_component[0]["MolecularWeight"]["endpoint"][0]["transform"]["coef_se"] = self.mw_transform_coef_se
                csv_data_column_label = get_csv_data_column_label(self.mw_name, self.selected_property)
            case "ta": # Tanimoto distance
                scoring_component = tanimoto_config
                scoring_component[0]["TanimotoDistance"]["endpoint"][0]["name"] = self.tanimoto_name
                scoring_component[0]["TanimotoDistance"]["endpoint"][0]["weight"] = self.tanimoto_weight
                scoring_component[0]["TanimotoDistance"]["endpoint"][0]["params"]["smiles"] = self.tanimoto_smiles
                scoring_component[0]["TanimotoDistance"]["endpoint"][0]["params"]["radius"] = self.tanimoto_radius
                scoring_component[0]["TanimotoDistance"]["endpoint"][0]["params"]["use_counts"] = self.tanimoto_use_counts
                scoring_component[0]["TanimotoDistance"]["endpoint"][0]["params"]["use_features"] = self.tanimoto_use_features
                csv_data_column_label = get_csv_data_column_label(self.tanimoto_name, self.selected_property)
            case "pm": # PMI
                scoring_component = pmi_config
                scoring_component[0]["pmi"]["name"] = self.pmi_name
                scoring_component[0]["pmi"]["endpoint"][0]["weight"] = self.pmi_weight_1
                scoring_component[0]["pmi"]["endpoint"][0]["params"]["property"] = self.pmi_property_1
                scoring_component[0]["pmi"]["endpoint"][1]["weight"] = self.pmi_weight_2
                scoring_component[0]["pmi"]["endpoint"][1]["params"]["property"] = self.pmi_property_2
                match self.selected_property:
                    case "pmi":
                        csv_data_column_label = "pmi"
                    case "pmi2":
                        csv_data_column_label = "pmi.2"
                    case "pmi_raw":
                        csv_data_column_label = "pmi (raw)"
                    case "pmi2_raw":
                        csv_data_column_label = "pmi (raw).2"
                    case _:
                        return['Error: PMI labels not found']
            case _:
                return['Error: Undefined property']
                sys.exit()
        """Pop the scoring_config into the runner config object and execute the runner"""
        scoring_config["scoring"]["component"] = scoring_component
        runner_input_config = extract_sections(scoring_config)
        runner = getattr(runmodes, "run_scoring")
        runner(input_config=runner_input_config,
               device=dev,
               tb_logdir=tb,
               responder_config=resp,
               write_config=write,
              )
        """Get the correct column data from CSV file for return"""
        with open(score_output_file.name, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            first_row = next(reader, None)
            if first_row:
                results = first_row[csv_data_column_label]
            else:
                return['Error: CSV file error'] 
        """Delete the temp files """
        nuke_file(score_input_file.name)
        nuke_file(score_output_file.name)
        return results

# Register the function in global scope and crank up the server
Reinvent4Predictor.register()

if __name__ == "__main__":
    # start the server
    start_server(port=8080)
