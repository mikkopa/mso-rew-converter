# MSO to REW Filter Converter

A Python tool to convert Multi-Sub Optimizer (MSO) filter configurations to REW (Room EQ Wizard) / StormAudio compatible format.

## Overview

This tool parses MSO output files and converts Parametric EQ and All-Pass filters into a format that can be imported into REW or StormAudio processors. It handles individual channel filters as well as shared subwoofer filters with flexible configuration options.

## Features

- **Two-stage parsing**: Accurately extracts filters from MSO channel blocks
- **Multiple filter types**: Supports Parametric EQ (RBJ) and All-Pass filters
- **Q value selection**: Choose between RBJ or Classic Q values
- **Filter type control**: Include/exclude specific filter types
- **Flexible output**: Separate files per channel or combined with shared filters
- **Professional format**: Generates REW/StormAudio compatible filter files

## Supported Filter Types

### Currently Supported
- **Parametric EQ (RBJ)**: Converted to Bell filters
- **All-Pass Second-Order**: Converted to All Pass filters

### Automatically Excluded (configurable)
- **Gain Block**: Not directly convertible to EQ format
- **Delay Block**: Not directly convertible to EQ format

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.6+ installed
3. No additional dependencies required (uses only standard library)

```bash
git clone <repository-url>
cd mso-rew-converter
```

## Usage

Save MSO Filters (abbreviated) to a text file. That file is used as an input to this converter.

### Basic Usage

In Windows use `python` instead of `python3`

```bash
python convert.py input_file.txt output_folder
```

In Mac or Linux:
```bash
python3 convert.py input_file.txt output_folder
```

### Common Examples

```bash
# Convert only Parametric EQ filters (default)
python3 convert.py mso-filters-summary-abbreviated.txt output

# Include both Parametric EQ and All-Pass filters
python3 convert.py mso-filters-summary-abbreviated.txt output --include-types "Parametric EQ" "All-Pass"

# Use Classic Q values instead of RBJ
python3 convert.py mso-filters-summary-abbreviated.txt output --q-type classic

# Combine shared subwoofer filters with each channel
python3 convert.py mso-filters-summary-abbreviated.txt output --combine-shared

# Custom equalizer name
python3 convert.py mso-filters-summary-abbreviated.txt output --equaliser "MyProcessor"
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_file` | Path to MSO source file | Required |
| `output_folder` | Output directory for converted files | Required |
| `--equaliser` | Equalizer name in output files | `StormAudio` |
| `--q-type` | Q value type: `rbj` or `classic` | `rbj` |
| `--include-types` | Filter types to include | `Parametric EQ` `All-Pass` |
| `--exclude-types` | Filter types to exclude | `Gain Block` `Delay Block` |
| `--combine-shared` | Combine shared filters with channel filters | `False` |

## Input Format

The tool expects MSO output files with the following structure:

```
Channel: "FL"
FL1: Parametric EQ (RBJ)
Parameter "Center freq (Hz)" = 52.9284
Parameter "Boost (dB)" = -2.56499
Parameter "Q (RBJ)" = 11.0387
"Classic" Q = 12.7951

FL9: All-Pass Second-Order
Parameter "Freq of 180 deg phase (Hz)" = 32.1576
Parameter "All-pass Q" = 0.500044
End Channel: "FL"

Shared sub channel:
FL45: Parametric EQ (RBJ)
Parameter "Center freq (Hz)" = 74.8662
Parameter "Boost (dB)" = -7.66676
Parameter "Q (RBJ)" = 3.59375
"Classic" Q = 5.5875
End shared sub channel
```

## Output Format

### Parametric EQ Filters
```
Filter 1: ON Bell Fc 52.9284 Hz Gain -2.56499 dB Q 11.0387
```

### All-Pass Filters
```
Filter 9: ON All Pass Order 2 Fc 32.1576 Hz Gain 0 dB Q 0.500044
```

### Output Files

#### Default Mode (Separate Files)
- `FL_filters.txt` - Front Left channel
- `FR_filters.txt` - Front Right channel  
- `RL_filters.txt` - Rear Left channel
- `RR_filters.txt` - Rear Right channel
- `shared_sub_filters.txt` - Shared subwoofer filters

#### Combined Mode (`--combine-shared`)
- `FL_filters.txt` - Shared + Front Left filters
- `FR_filters.txt` - Shared + Front Right filters
- `RL_filters.txt` - Shared + Rear Left filters
- `RR_filters.txt` - Shared + Rear Right filters

## Examples

### Example 1: Basic Conversion
```bash
python3 convert.py mso_output.txt converted_filters
```
Output: Separate files with Parametric EQ and All-Pass filters using RBJ Q values.

### Example 2: Combined Output for Hardware Implementation
```bash
python3 convert.py mso_output.txt hardware_config --combine-shared --equaliser "My Processor"
```
Output: Each channel file contains shared subwoofer filters followed by channel-specific filters.

### Example 3: Classic Q Values Only
```bash
python3 convert.py mso_output.txt classic_output --q-type classic --include-types "Parametric EQ"
```
Output: Only Parametric EQ filters using Classic Q values.

## Technical Details

### Q Value Types
- **RBJ Q**: Uses `Parameter "Q (RBJ)"` values from MSO output. This is compatible with StormAudio PEQ.
- **Classic Q**: Uses `"Classic" Q` values from MSO output

### Filter Processing
1. **Stage 1**: Extract channel blocks using regex pattern matching
2. **Stage 2**: Parse individual filters within each block
3. **Type filtering**: Include/exclude filters based on type
4. **Format conversion**: Convert to REW/StormAudio format
5. **File generation**: Create separate or combined output files

### Two-Stage Parsing
The tool uses a robust two-stage parsing approach:
1. First stage extracts content between channel boundaries (`Channel: "XX"` to `End Channel: "XX"`)
2. Second stage parses individual filter blocks within each channel

## Troubleshooting

### Common Issues

**No filters found**
- Check that input file contains proper MSO format
- Verify filter types are included (not excluded)
- Ensure channel boundaries are properly formatted

**Missing shared filters**
- Verify "Shared sub channel:" section exists in input
- Check that shared filters aren't being excluded by type

**Incorrect Q values**
- Use `--q-type classic` if RBJ values seem incorrect
- Both Q types are available in MSO output

### Debug Output
The tool provides detailed output showing:
- Filter types being processed
- Number of filters found per channel
- Total filters processed vs exported

## License

This project is open source. Please check the LICENSE file for details.

## Version History

- **v1.0**: Initial release with Parametric EQ support
- **v1.1**: Added All-Pass filter support
- **v1.2**: Added combine-shared option and improved parsing

## Acknowledgments

- Multi-Sub Optimizer (MSO) by Andy C
- Room EQ Wizard (REW) by John Mulcahy
- StormAudio for filter format specifications
