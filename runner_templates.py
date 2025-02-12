scoring_config = {
    "run_type": "scoring",
    "device": "cpu",
    "use_cuda": True,
    "tb_logdir": None,
    "json_out_config": "_scoring.json",
    "parameters": {
        "smiles_file": "compounds.smi",
        "output_csv": "scoring.scv",
        "smiles_column": "SMILES",
        "standardize_smiles": True
    },
    "scoring": {
        "type": "geometric_mean",
        "parallel": False,
        "component": [],
        "filename": None
    },
    "scheduler": None,
    "responder": None,
    "stage": None,
    "learning_strategy": None,
    "diversity_filter": None,
    "inception": None
}

custom_alerts_config = [{
                "custom_alerts": {
                    "endpoint": [
                        {
                            "name": "Alerts",
                            "params": {
                                "smarts": ["[*;r10]"]
                            }
                        }
                    ]
                }
            }]

qed_config =             [{
                "QED": {
                    "endpoint": [
                        {
                            "name": "QED",
                            "weight": 0.25 
                        }
                    ]
                }
            }]

molecular_weight_config =             [{
                "MolecularWeight": {
                    "endpoint": [
                        {
                            "name": "MW",
                            "weight": 0.25,
                            "transform": {
                                "type": "double_sigmoid",
                                "high": 500.0,
                                "low": 200.0,
                                "coef_div": 500.0,
                                "coef_si": 20.0,
                                "coef_se": 20.0
                            }
                        }
                    ]
                }
            }]

tanimoto_config =            [ {
                "TanimotoDistance": {
                    "endpoint": [
                        {
                            "name": "Tanimoto similarity ECF6",
                            "weight": 0.1,
                            "params": {
                                "smiles": [],
                                "radius": 3 ,
                                "use_counts": True,
                                "use_features": True
                            }
                        }
                    ]
                }
            }]

pmi_config =             [{
                "pmi": {
                    "name": "PMI 3D-likeness",
                    "endpoint": [
                        {
                            "weight": 0.79,
                            "params": {
                                "property": "npr1"
                            }
                        },
                        {
                            "weight": 0.21,
                            "params": {
                                "property": "npr2"
                            }
                        }
                    ]
                }
            }]
