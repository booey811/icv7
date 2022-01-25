standard_checks = {
    'Bluetooth': 'bluetooth',  # Bluetooth Column
    'Ear Speaker': 'earpiece',  # Earpiece & Mesh Column
    'Flashlight': 'flashlight',  # Flashlight Column TODO: Mapping
    'Flip Switch': 'mute_vol',  # Mute/Vol Buttons Column
    'Front Camera': 'front_cam',  # Front Camera Column
    'Front Microphone': 'siri',  # Siri Column
    'Front Video Camera': 'front_cam',  # Front Camera Column
    'Front Camera Quality': 'front_cam',  # Front Camera Column
    'Loud Speaker': 'loudspeaker',  # Loudspeaker Column
    'Microphone': 'mic',  # Microphone Column
    'Network Connectivity': None,  # HAS NO COLUMN
    'Power Button': 'power',  # Power Button Column
    'Proximity Sensor': 'front_cam',  # Front Camera Column
    'Rear Camera': 'rear_cam',  # Rear Camera Column
    'Rear Camera Quality': 'rear_cam',  # Rear Camera Column
    'Rear Video Camera': 'rear_cam',  # Rear Camera Column
    'Telephoto Camera': 'rear_cam',  # Rear Camera Column
    'Telephoto Camera Quality': 'rear_cam',  # Rear Camera Column
    'Vibration': 'haptic',  # Haptic Column
    'Video Microphone': 'power',  # Power Button Column
    'Volume Down Button': 'mute_vol',  # Mute/Volume Column
    'Volume Up Button': 'mute_vol',  # Mute/Volume Column
    'Wifi': 'wifi',  # Wifi Column
    'Face ID': 'face_id',  # Face ID Check Column
    'Glass Cracked': 'screen',  # Front Screen Column
    'LCD': 'screen',  # Front Screen Column
    'NFC': 'nfc',  # NFC Column
    "Force Touch": "screen"  # Screen Column
}

convert_to_main = {
    'Battery': '71',
    'Bluetooth': '93',
    'Charging Port': '54',
    'Ear Speaker': '73',
    'Face ID': '99',
    'Front Camera': '76',
    'Front Video Camera': "76",
    'Front Camera Quality': "76",
    'Front Screen': '133',
    'Force Touch': '133',
    'Glass Cracked': '133',
    'LCD': '133',
    'Front Screen (LG)': '83',
    'Front Screen (Tosh)': '84',
    'Front Screen Universal': '69',
    'Vibration': '78',
    'Headphone Jack': '67',
    'Loud Speaker': '88',
    'Mesh': '132',
    'Microphone': '66',
    'Flip Switch': '77',
    'NFC': '85',
    'Power Button': '36',
    'Video Microphone': '36',
    'Proximity Sensor': '107',
    'Rear Camera': '70',
    'Rear Camera Quality': '70',
    'Rear Video Camera': '70',
    'Telephoto Camera': '70',
    'Telephoto Camera Quality': '70',
    'Rear Glass': '82',
    'Rear Housing': '65',
    'Rear Lens': '7',
    'Rear Microphone': '142',
    'Front Microphone': '102',
    'Volume Down Button': '75',
    'Volume Up Button': '75',
    'Wifi': '18',
    'Wireless Charging': '101',

    '101': 'Wireless Charging',
    '102': 'Siri',
    '107': 'Proximity Sensor',
    '132': 'Mesh',
    '133': 'Front Screen',
    '142': 'Rear Microphone',
    '18': 'Wifi Module',
    '30': 'LCD',
    '36': 'Power Button',
    '54': 'Charging Port',
    '65': 'Rear Housing',
    '66': 'Microphone',
    '67': 'Headphone Jack',
    '69': 'Front Screen Universal',
    '7': 'Rear Lens',
    '70': 'Rear Camera',
    '71': 'Battery',
    '73': 'Earpiece',
    '75': 'Volume Button',
    '76': 'Front Camera',
    '77': 'Mute Button',
    '78': 'Haptic',
    '82': 'Rear Glass',
    '83': 'Front Screen (LG)',
    '84': 'Front Screen (Tosh)',
    '85': 'NFC Module',
    '88': 'Loudspeaker',
    '93': 'Bluetooth Module',
    '99': 'Face ID'
}
