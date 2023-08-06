from parselmouth.praat import call
import Voicelab.toolkits.Voicelab as Voicelab

# List of all available operations the user can perform as well as their associated function node
available_functions = {
    "Measure Duration": Voicelab.MeasureDurationNode("Measure Duration"),
    "Measure Pitch": Voicelab.MeasurePitchNode("Measure Pitch"),
    "Measure Subharmonics": Voicelab.MeasureSHRPNode("Measure Subharmonics"),
    # "Measure Pitch Yin": Voicelab.MeasurePitchYinNode("Measure Pitch Yin"),
    # "Measure Pitch Crepe": Voicelab.MeasurePitchCrepeNode("Measure Pitch Crepe"),
    "Measure Harmonics-to-Noise-Ratio": Voicelab.MeasureHarmonicityNode(
        "Measure Harmonics-to-Noise-Ratio"
    ),
    "Measure Jitter": Voicelab.MeasureJitterNode("Measure Jitter"),
    "Measure Shimmer": Voicelab.MeasureShimmerNode("Measure Shimmer"),
    "Measure Cepstral Peak Prominance (CPP)": Voicelab.MeasureCPPNode(
        "Measure Cepstral Peak Prominance (CPP)"
    ),
    "Measure Formants": Voicelab.MeasureFormantNode("Measure Formants"),
    # 'Measure Formants Position': Voicelab.MeasureFormantPositionsNode('Measure Formants Position'),
    "Measure Vocal Tract Estimates": Voicelab.MeasureVocalTractEstimatesNode(
        "Measure Vocal Tract Estimates"
    ),
    "Measure Intensity": Voicelab.MeasureIntensityNode("Measure Intensity"),
    "Measure Speech Rate": Voicelab.MeasureSpeechRateNode("Measure Speech Rate"),
    "Measure Signal-to-Noise Ratio": Voicelab.MeasureSNRNode(
        "Measure Signal-to-Noise Ratio"
    ),

    "Measure LTAS": Voicelab.MeasureLTASNode("Measure LTAS"),

    "Measure Spectral Tilt": Voicelab.MeasureSpectralTiltNode("Measure Spectral Tilt"),
    "Measure RMS Energy": Voicelab.MeasureEnergyNode("Measure RMS Energy"),
    "Measure Spectral Shape": Voicelab.MeasureSpectralShapeNode("Measure Spectral Shape"),
    "TEVA (Tracheoesophageal Voice Analysis)": Voicelab.TEVANode("TEVA (Tracheoesophageal Voice Analysis)"),

    "Manipulate Pitch Lower": Voicelab.ManipulatePitchLowerNode(
        "Manipulate Pitch Lower"
    ),
    "Manipulate Pitch Higher": Voicelab.ManipulatePitchHigherNode(
        "Manipulate Pitch Higher"
    ),
    #"Manipulate Formants": Voicelab.ManipulateFormantsNode("Manipulate Formants"),
    "Manipulate Formants Lower": Voicelab.ManipulateLowerFormantsNode("Manipulate Formants Lower"),
    "Manipulate Formants Higher": Voicelab.ManipulateRaiseFormantsNode("Manipulate Formants Higher"),
    #"Manipulate Pitch And Formants": Voicelab.ManipulatePitchAndFormantsNode(
    #    "Manipulate Pitch And Formants"
    #),
    "Manipulate Pitch And Formants Lower": Voicelab.ManipulateLowerPitchAndFormantsNode(
            "Manipulate Pitch And Formants Lower"
        ),
    "Manipulate Pitch And Formants Higher": Voicelab.ManipulateRaisePitchAndFormantsNode(
            "Manipulate Pitch And Formants Higher"
        ),
    "Resample Sounds": Voicelab.ResampleSoundsNode("Resample Sounds"),
    "Reverse Sounds": Voicelab.ReverseSoundsNode("Reverse Sounds"),
    "Scale Intensity (RMS)": Voicelab.ScaleIntensityNode("Scale Intensity (RMS)"),
    "Create Spectrograms": Voicelab.VisualizeVoiceNode("Create Spectrograms"),
    "Create F1F2 Plot": Voicelab.F1F2PlotNode("Create F1F2 Plot"),
}

# List of default functions that will be performed.
# NOTE: Excel limits sheet titles to 31 characters, since these are used as the titles of the sheets
# anything longer than 31 characters will be truncated
# this doesn't have to be in the same order as the list above
default_functions = [
    "Measure Duration",
    "Measure Pitch",
    "Measure Subharmonics",
    #"Measure Pitch Yin",
    # "Measure Pitch Crepe",
    "Measure Formants",
    # "Measure Signal-to-Noise Ratio",
    "Measure Harmonics-to-Noise-Ratio",
    "Measure Cepstral Peak Prominance (CPP)",
    "Measure Jitter",
    "Measure Shimmer",
    "Measure Intensity",
    "Measure RMS Energy",
    "Measure Spectral Tilt",
    # "Measure LTAS",
    "Measure Spectral Shape",
    # "TEVA (Tracheoesophageal Voice Analysis)",
    # 'Measure Speech Rate',
    "Measure Vocal Tract Estimates",
    # 'Manipulate Formants Lower',
    # 'Manipulate Formants Higher',
    # 'Manipulate Pitch And Formants Lower',
    # 'Manipulate Pitch Lower',
    # 'Manipulate Pitch Higher',
    # 'Scale Intensity (RMS)'
    # 'Resample Sounds'
    # 'Reverse Sounds'
    # 'Create Spectrograms',
    # "Create F1F2 Plot",
]

# list of nodes that have visualizable return values and a list naming the values to visualize
visualize_list = {
    "Measure Pitch": "Pitch",
    "Measure Intensity": "Intensity",
    "Measure Formants": "Formants",
}

# these are the types of values that are allowed to display, this is to prevent things like
# sound objects printed to screen. Adding a new type here will let it show up in the results
display_whitelist = [int, float, str]

# Simple way to define upstream data requirements. Basically replacing the interactive gui
# Function requirements should be written as:

# 'CHILD FUNCTION NAME': [(PARENT FUNCTION NAME, VARIABLE NAME), ...]
function_requirements = {
    # Measure formant positions requires that we first measure the pitch and formants
    "Measure Formants Position": [
        ("Measure Formants", "Formants"),
        ("Measure Pitch", "Pitch"),
        ("Measure Pitch", "Pitch Floor"),
        ("Measure Pitch", "Pitch Ceiling"),
    ],
    # Measure formant positions requires that we first measure the pitch and formants
    "Measure Vocal Tract Estimates": [
        ("Measure Formants", "F1 Mean"),
        ("Measure Formants", "F2 Mean"),
        ("Measure Formants", "F3 Mean"),
        ("Measure Formants", "F4 Mean"),
        ("Measure Formants", "F1 Median"),
        ("Measure Formants", "F2 Median"),
        ("Measure Formants", "F3 Median"),
        ("Measure Formants", "F4 Median"),
        ("Measure Pitch", "Pitch"),
        ],

    #"Measure Formants Sweep":[
    #    ("Measure Formants", "F1 Mean"),
    #    ("Measure Formants", "F2 Mean"),
    #    ("Measure Formants", "F3 Mean"),
    #    ("Measure Formants", "F4 Mean"),
    #],

    "Measure Shimmer": [
        ("Measure Pitch", "Pitch Floor"),
        ("Measure Pitch", "Pitch Ceiling"),

    ],
    "Measure Cepstral Peak Prominance (CPP)": [
        ("Measure Pitch", "Pitch Floor"),
        ("Measure Pitch", "Pitch Ceiling"),

    ],
    "Measure Formants": [
        ("Measure Pitch", "Pitch Floor"),
        ("Measure Pitch", "Pitch Ceiling"),

    ],
    "Measure Jitter": [
        ("Measure Pitch", "Pitch Floor"),
        ("Measure Pitch", "Pitch Ceiling"),

    ],
    "Measure Harmonicity": [
        ("Measure Pitch", "Pitch Floor"),
        ("Measure Pitch", "Pitch Ceiling"),

    ],
    "Create Spectrograms": [
        ("Measure Formants", "Formants"),
        ("Measure Intensity", "Intensity"),
        ("Measure Pitch", "Pitch"),
        ("Measure Pitch", "Pitch Floor"),
        ("Measure Pitch", "Pitch Ceiling"),
    ],

    "Create F1F2 Plot": [
        ("Measure Formants", "F1 Mean"),
        ("Measure Formants", "F2 Mean"),
        ("Measure Formants", "F3 Mean"),
        ("Measure Formants", "F4 Mean"),
    ],
}
