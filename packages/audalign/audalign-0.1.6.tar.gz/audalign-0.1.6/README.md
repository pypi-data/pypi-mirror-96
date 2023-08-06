# Audalign
Python package for aligning audio files using audio fingerprinting or visual alignment techniques.

This package offers tools to align many recordings of the same event. This is primarily accomplished with fingerprinting, though where fingerprinting fails, visual alignment techniques can be used to get a closer result.

Alignment consists of a dictionary containing alignment data for all files in a given directory. If an output directory is given, silence is placed before all files in the target directory so that all will automatically be aligned and writen to the output directory along with an audio file containing the sum of all audio. 

All fingerprints are stored in memory and must be saved to disk with the save_fingerprinted_files method in order to persist them.

Regular file recogniton can also be done with Audalign similar to dejavu but held in memory. 

---

This package is also primarirly focused on accuracy of alignments and has several accuracy settings. Parameters for visual alignment can be adjusted. Fingerprinting parameters can be generally set to get consistent results, but visual alignment requires case by case adjustment.

Noisereduce is very useful for this application and a wrapper is implemented for ease of use.

Waveform alignment techniques are not implemented, though they could be in the future.

## Installation

Install from PyPI:

Don't forget to install ffmpeg/avlib (Below in the Readme)!

```bash
pip install audalign
```

OR


```bash
git clone https://github.com/benfmiller/audalign.git
cd audalign/
pip install audalign
```

OR

Download and extract audalign then
```bash
pip install audalign
```
in the directory

## Aligning

```python
import audalign
ada = audalign.Audalign()

print(ada.align("target/folder/", destination_path="write/alignments/to/folder"))
# or
print(ada.target_align(
    "target/files",
    "target/folder/",
    destination_path="write/alignments/to/folder",
    ))

# For Visual
print(ada.target_align(
    "target/files",
    "target/folder/",
    destination_path="write/alignments/to/folder",
    use_fingerprints=False,
    ))
# volume_threshold might need to be adjusted depending on the file
```
Returns dictionary of each file recognized and best alignment. Also returns match info dictionary of each recognition in the folder

You can specify a destination folder to write the aligned files with the appropriate length of silence added to the front.

Target align only aligns with one target file rather than finding the file with the most and best matches.

## Fingerprinting

Audalign is mostly built on fingerprinting.

```python
import audalign
ada = audalign.Audalign()

ada.fingerprint_file("test_file.wav")

# or

ada.fingerprint_directory("audio/directory")
```
fingerprints are stored in ada and can be saved by 

```python
ada.save_fingerprinted_files("save_file.json") # or .pickle
# or loaded with 
ada.load_fingerprinted_files("save_file.json") # or .pickle
```
All formats that ffmpeg or libav support are supported here.

## Recognizing

Alignments are accomplished with recognizing

```python
# Only returns matches with total fingerprint matches greater than 50 within 5 second windows
print(ada.recognize("matching_file.mp3", filter_matches=50, locality=5))

# For Visual
print(ada.visrecognize(
    target_file_path="target_file.mp3", against_file_path="against_file.mp3"
    ))
```
File doesn't have to be fingerprinted already. If it is, the file is not re-fingerprinted

Returns dictionary match time and match info. Match info is a dictionary of each file it recognized with. Each file is a dictionary of match information.

## Other Functions

```python
ada.remove_noise_file(
    "target/file",
    "5", # noise start in seconds
    "20", # noise end in seconds
    "destination/file",
    alt_noise_filepath="different/sound/file",
    prop_decrease="0.5", # If you want noise half reduced
)

ada.remove_noise_directory(
    "target/directory/",
    "noise/file",
    "5", # noise start in seconds
    "20", # noise end in seconds
    "destination/directory",
    prop_decrease="0.5", # If you want noise half reduced
)

ada.plot("file.wav") # Plots spectrogram with peaks overlaid
ada.convert_audio_file("audio.wav", "audio.mp3") # Also convert video file to audio file
```
## Audalign Functions

```python
ada.set_multiprocessing(False) # If you want single threaded fingerprinting
ada.set_num_processors(4) # However many processors you have.
ada.set_accuracy(1) # from 1-4, sets fingerprinting variables for different levels of accuracy
ada.set_hash_style("base") #you can use "base" "base_three" "panako" "panako_mod"
ada.set_freq_threshold(100) # ignores frequencies below value. Max value is 2049. Not Hertz
```


## Getting ffmpeg set up

You can use **ffmpeg or libav**.

Mac (using [homebrew](http://brew.sh)):

```bash
# ffmpeg
brew install ffmpeg --with-libvorbis --with-sdl2 --with-theora

####    OR    #####

# libav
brew install libav --with-libvorbis --with-sdl --with-theora
```

Linux (using apt):

```bash
# ffmpeg
apt-get install ffmpeg libavcodec-extra

####    OR    #####

# libav
apt-get install libav-tools libavcodec-extra
```

Windows:

1. Download and extract ffmpeg from [Windows binaries provided here](https://ffmpeg.org/download.html).
2. Add the ffmpeg `/bin` folder to your PATH environment variable

OR

1. Download and extract libav from [Windows binaries provided here](http://builds.libav.org/windows/).
2. Add the libav `/bin` folder to your PATH environment variable
