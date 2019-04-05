MODEL_PARAMS = {
    "aggregationInfo": {
        "hours": 1,
        "microseconds": 0,
        "seconds": 0,
        "fields": [
            [
                "c1",
                "sum"
            ],
            [
                "c0",
                "first"
            ]
        ],
        "weeks": 0,
        "months": 0,
        "minutes": 0,
        "days": 0,
        "milliseconds": 0,
        "years": 0
    },
    "model": "HTMPrediction",
    "version": 1,
    "predictAheadTime": null,
    "modelParams": {
        "sensorParams": {
            "verbosity": 0,
            "encoders": {
                "total_utilization": {
                    "maxval": 100.0,
                    "fieldname": "CPT",
                    "name": "consumption",
                    "w": 21,
                    "clipInput": true,
                    "minval": 0.0,
                    "type": "ScalarEncoder",
                    "n": 50
                },
                "timestamp_weekend": null,
                "timestamp_timeOfDay": {
                    "type": "DateEncoder",
                    "timeOfDay": [
                        21,
                        9.5
                    ],
                    "fieldname": "timestamp",
                    "name": "timestamp_timeOfDay"
                },
                "timestamp_dayOfWeek": null
            },
            "sensorAutoReset": null
        },
        "clEnable": false,
        "spParams": {
            "columnCount": 2048,
            "spVerbosity": 0,
            "spatialImp": "cpp",
            "synPermConnected": 0.1,
            "seed": 1956,
            "numActiveColumnsPerInhArea": 40,
            "globalInhibition": 1,
            "inputWidth": 0,
            "synPermInactiveDec": 0.0005,
            "synPermActiveInc": 0.0001,
            "potentialPct": 0.8,
            "boostStrength": 0.0
        },
        "spEnable": true,
        "clParams": null,
        "inferenceType": "TemporalAnomaly",
        "anomalyParams": {
            "anomalyCacheRecords": null,
            "autoDetectThreshold": null,
            "autoDetectWaitRecords": 2184
        },
        "tmParams": {
            "columnCount": 2048,
            "activationThreshold": 12,
            "pamLength": 3,
            "cellsPerColumn": 32,
            "permanenceInc": 0.1,
            "minThreshold": 9,
            "verbosity": 0,
            "maxSynapsesPerSegment": 32,
            "outputType": "normal",
            "initialPerm": 0.21,
            "globalDecay": 0.0,
            "maxAge": 0,
            "permanenceDec": 0.1,
            "seed": 1960,
            "newSynapseCount": 20,
            "maxSegmentsPerCell": 128,
            "temporalImp": "cpp",
            "inputWidth": 2048
        },
        "tmEnable": true,
        "trainSPNetOnlyIfRequested": false
    }
}