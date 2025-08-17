import re
import os
import argparse
from datetime import datetime

def parse_mso_file(input_file, q_type='rbj', included_types=None, excluded_types=None):
    """Parse MSO file and extract filters by channel using two-stage parsing."""
    with open(input_file, 'r') as file:
        content = file.read()
    
    channels = {}
    shared_sub = []
    
    # Stage 1: Extract channel blocks
    channel_blocks = extract_channel_blocks(content)
    shared_block = extract_shared_sub_block(content)
    
    # Stage 2: Parse filters within each block
    for channel_name, channel_content in channel_blocks.items():
        channel_filters = parse_filters_from_text(channel_content, q_type, included_types, excluded_types)
        if channel_filters:
            channels[channel_name] = channel_filters
    
    if shared_block:
        shared_sub = parse_filters_from_text(shared_block, q_type, included_types, excluded_types)
    
    return channels, shared_sub

def extract_channel_blocks(content):
    """Stage 1: Extract content blocks for each individual channel."""
    channels = {}
    
    # Find all individual channels
    channel_pattern = r'Channel: "([^"]+)"(.*?)End Channel: "\1"'
    matches = re.findall(channel_pattern, content, re.DOTALL)
    
    for channel_name, channel_content in matches:
        channels[channel_name] = channel_content.strip()
    
    return channels

def extract_shared_sub_block(content):
    """Stage 1: Extract shared sub channel block."""
    shared_start = content.find('Shared sub channel:')
    shared_end = content.find('End shared sub channel')
    
    if shared_start != -1 and shared_end != -1:
        return content[shared_start:shared_end].strip()
    
    return None

def parse_filters_from_text(text, q_type='rbj', included_types=None, excluded_types=None):
    """Stage 2: Parse all filter types from text content."""
    if included_types is None:
        included_types = ['Parametric EQ']
    if excluded_types is None:
        excluded_types = ['Gain Block', 'Delay Block']
    
    filters = []
    
    # Pattern to match filter blocks - each filter starts with FL## and continues until the next FL## or end
    filter_blocks = re.split(r'\n(?=FL\d+:)', text)
    
    for block in filter_blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if not lines:
            continue
            
        # First line contains filter name and type
        first_line = lines[0]
        filter_match = re.match(r'(FL\d+): (.+)', first_line)
        
        if not filter_match:
            continue
            
        filter_name = filter_match.group(1)
        filter_type = filter_match.group(2).strip()
        
        # Check if this filter type should be included
        should_include = False
        for included_type in included_types:
            if included_type.lower() in filter_type.lower():
                should_include = True
                break
        
        # Check if this filter type should be excluded
        for excluded_type in excluded_types:
            if excluded_type.lower() in filter_type.lower():
                should_include = False
                break
        
        if not should_include:
            continue
        
        # Join all parameter lines for this filter
        parameters = '\n'.join(lines[1:])
        
        # Parse parameters based on filter type
        if 'Parametric EQ' in filter_type:
            filter_data = parse_parametric_eq_parameters(filter_name, filter_type, parameters, q_type)
            if filter_data:
                filters.append(filter_data)
        elif 'All-Pass' in filter_type:
            filter_data = parse_allpass_parameters(filter_name, filter_type, parameters)
            if filter_data:
                filters.append(filter_data)
        # Add more filter types here as needed
    
    return filters

def parse_parametric_eq_parameters(filter_name, filter_type, parameters, q_type='rbj'):
    """Parse Parametric EQ parameters."""
    freq_match = re.search(r'Parameter "Center freq \(Hz\)" = ([\d.]+)', parameters)
    gain_match = re.search(r'Parameter "Boost \(dB\)" = ([-\d.]+)', parameters)
    q_rbj_match = re.search(r'Parameter "Q \(RBJ\)" = ([\d.]+)', parameters)
    q_classic_match = re.search(r'"Classic" Q = ([\d.]+)', parameters)
    
    if not (freq_match and gain_match and q_rbj_match):
        return None
    
    freq = float(freq_match.group(1))
    gain = float(gain_match.group(1))
    q_rbj = float(q_rbj_match.group(1))
    q_classic = float(q_classic_match.group(1)) if q_classic_match else q_rbj
    
    # Select Q value based on q_type parameter
    q_value = q_classic if q_type == 'classic' else q_rbj
    
    return {
        'name': filter_name,
        'type': filter_type,
        'freq': freq,
        'gain': gain,
        'q': q_value,
        'q_rbj': q_rbj,
        'q_classic': q_classic
    }

def parse_allpass_parameters(filter_name, filter_type, parameters):
    """Parse All-Pass filter parameters."""
    freq_match = re.search(r'Parameter "Freq of 180 deg phase \(Hz\)" = ([\d.]+)', parameters)
    q_match = re.search(r'Parameter "All-pass Q" = ([\d.]+)', parameters)
    
    if not (freq_match and q_match):
        return None
    
    return {
        'name': filter_name,
        'type': filter_type,
        'freq': float(freq_match.group(1)),
        'q': float(q_match.group(1))
    }

def write_storm_audio_format(filters, output_file, channel_name="", equaliser_name="StormAudio"):
    """Write filters in StormAudio format."""
    
    with open(output_file, 'w') as file:
        file.write("Filter Settings file\n\n")
        file.write(f"Dated:{datetime.now().strftime('%Y%m%d')}\n\n")
        file.write(f"Equaliser: {equaliser_name}\n")
        if channel_name:
            file.write(f"Channel: {channel_name}\n")
        file.write("\n")
        
        filter_count = 1
        for filter_data in filters:
            if 'Parametric EQ' in filter_data['type']:
                file.write(f"Filter {filter_count}: ON Bell Fc {filter_data['freq']} Hz Gain {filter_data['gain']} dB Q {filter_data['q']}\n")
                filter_count += 1
            elif 'All-Pass' in filter_data['type']:
                # Extract order from filter type (e.g., "All-Pass Second-Order" -> "2")
                order = "2"  # Default to 2nd order
                if "Second-Order" in filter_data['type']:
                    order = "2"
                elif "First-Order" in filter_data['type']:
                    order = "1"
                elif "Third-Order" in filter_data['type']:
                    order = "3"
                elif "Fourth-Order" in filter_data['type']:
                    order = "4"
                
                file.write(f"Filter {filter_count}: ON All Pass Order {order} Fc {filter_data['freq']} Hz Gain 0 dB Q {filter_data['q']}\n")
                filter_count += 1
            # Add more filter type conversions as needed

def convert_mso_to_storm_audio(input_file, output_folder, q_type='rbj', equaliser_name='StormAudio', included_types=None, excluded_types=None, combine_shared=False):
    """Main function to convert MSO format to StormAudio format."""
    try:
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Parse the MSO file
        channels, shared_sub = parse_mso_file(input_file, q_type, included_types, excluded_types)
        
        total_filters = 0
        total_exported = 0
        
        print(f"Using Q type: {q_type.upper()}")
        if included_types:
            print(f"Included filter types: {', '.join(included_types)}")
        if excluded_types:
            print(f"Excluded filter types: {', '.join(excluded_types)}")
        if combine_shared and shared_sub:
            print(f"Combining {len(shared_sub)} shared sub filters with individual channel filters")
        print("=" * 60)
        
        # Process individual channels
        for channel_name, filters in channels.items():
            if filters:
                # Combine shared sub filters with channel filters if requested
                if combine_shared and shared_sub:
                    # Shared filters first, then channel's own filters
                    combined_filters = shared_sub + filters
                    output_file = os.path.join(output_folder, f"{channel_name}_filters.txt")
                    write_storm_audio_format(combined_filters, output_file, channel_name, equaliser_name)
                    
                    print(f"Channel {channel_name}: {len(shared_sub)} shared + {len(filters)} channel = {len(combined_filters)} total filters exported to {channel_name}_filters.txt")
                    total_filters += len(filters)  # Count channel filters only once
                    total_exported += len(combined_filters)
                else:
                    # Write only channel-specific filters
                    output_file = os.path.join(output_folder, f"{channel_name}_filters.txt")
                    write_storm_audio_format(filters, output_file, channel_name, equaliser_name)
                    
                    print(f"Channel {channel_name}: {len(filters)} filters exported to {channel_name}_filters.txt")
                    total_filters += len(filters)
                    total_exported += len(filters)
        
        # Process shared sub channel (only if not combining with individual channels)
        if shared_sub and not combine_shared:
            output_file = os.path.join(output_folder, "shared_sub_filters.txt")
            write_storm_audio_format(shared_sub, output_file, "Shared Sub", equaliser_name)
            
            print(f"Shared Sub: {len(shared_sub)} filters exported to shared_sub_filters.txt")
            total_filters += len(shared_sub)
            total_exported += len(shared_sub)
        
        print("=" * 60)
        print(f"Conversion complete!")
        print(f"Total filters processed: {total_filters}")
        print(f"Total filters exported: {total_exported}")
        print(f"Output files saved to: {output_folder}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"Error during conversion: {e}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='''Convert MSO filters to REW/StormAudio format.

Currently supports:
- Parametric EQ filters
- All-Pass filters
                        
Note: Gain Block and Delay Block filters are ignored by default as they are not 
directly convertible to standard EQ filter formats.''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input_file', help='Path to the MSO source file')
    parser.add_argument('output_folder', help='Output folder for the converted files')
    parser.add_argument('--equaliser', default='StormAudio', help='Equaliser name (default: StormAudio)')
    parser.add_argument('--q-type', choices=['rbj', 'classic'], default='rbj', 
                        help='Q value type to use: rbj (default) or classic')
    parser.add_argument('--include-types', nargs='+', default=['Parametric EQ', 'All-Pass'],
                        help='Filter types to include (default: "Parametric EQ"). Example: --include-types "Parametric EQ" "All-Pass"')
    parser.add_argument('--exclude-types', nargs='+', default=['Gain Block', 'Delay Block'],
                        help='Filter types to exclude (default: "Gain Block" "Delay Block")')
    parser.add_argument('--combine-shared', action='store_true', 
                        help='Combine shared sub filters with each individual channel filter file. Shared filters are written first, then channel-specific filters. (default: False)')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return
    
    convert_mso_to_storm_audio(args.input_file, args.output_folder, args.q_type, args.equaliser, args.include_types, args.exclude_types, args.combine_shared)

if __name__ == "__main__":
    main()