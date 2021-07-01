Motion | PLEN Project Company Inc.
===============================================================================

Motion files (JSON) for PLEN:bit.

## Description of the Files

- `/motion-plenbit`: Default motion files for PLEN:bit

- `sdk`: Development kit for motion files
    - `device_map.json`: The file indicates the relationship between **'device name'** -> **'device address'**.
    - `metadata.py`: Metadata adding python script
    - `protocol.py`: python script
    - `motion-writer.py`: Motion writing python script
- `firmware_for_motion-writer.hex`: firmware

## Attention!

If you are using the servo motor shown as below, any latest version is OK.

<img src="./.assets/servo-motor.jpg" alt="Servo Motor" width="266">

## How to Use the SDK

1. Send `firmware_for_motion-writer.hex` to micro:bit
2. Execute `motion-writer.py` from console

### motion-writer.py

`python -u sdk/motion-writer.py -n <MOTION_FILES_NUMBER>`
- `-l`: Display the motion list and check the number

`python -u sdk/motion-writer.py -a`
- `-a`: write all motions.

`python -u sdk/motion-writer.py -m <MOTION_FILES_NUMBER>`
- `-m`: Write everything from the specified number. 

### python liblrary

```
    pip install pyserial
```

## Motion Editor

[Motion Editor](http://plen.jp/playground/motion-editor/#/?model=plen2-mini)


## Copyright (c) 2017 - 2020,
- [PLEN Project Company Inc.](https://plen.jp)
- Naohiro HAYAISHI
- Natsuo AKAZAWA
- Sho SUZUKI
- Mitsuhiro MIYAGUCHI

## Build Environment
### OS
- Windows 10 Pro 64 bit

### Programming Tools (SDK)
- ~~Python 2.7.17~~
- Python 3.8.5

## License
These files are released under [the MIT License](https://opensource.org/licenses/mit-license.php).