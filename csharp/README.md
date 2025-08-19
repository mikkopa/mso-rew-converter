# MSO to Storm Audio Converter - C# Implementation

This is a C# port of the MSO to REW converter, designed specifically for use in Blazor WASM applications.

## Features

- **Complete C# Implementation**: Full port of the Python converter logic
- **Blazor WASM Ready**: Optimized for client-side web applications
- **Same Options as Python Version**: All conversion options from the original Python implementation
- **Type-Safe Configuration**: Strongly-typed options class for easy configuration
- **UI-Friendly Classes**: Pre-built helpers for Blazor components

## Files

- **`MsoConverter.cs`** - Core conversion logic
- **`BlazorHelpers.cs`** - Blazor-specific helpers and UI models
- **`Program.cs`** - Console demo application
- **`MsoConverterComponent.razor`** - Example Blazor component

## Core Classes

### `ConversionOptions`
Configuration options for the conversion process:

```csharp
var options = new ConversionOptions
{
    QType = "rbj",                                              // "rbj" or "classic"
    IncludedTypes = new List<string> { "Parametric EQ", "All-Pass" },
    ExcludedTypes = new List<string> { "Gain Block", "Delay Block" },
    CombineShared = false,                                      // Combine shared filters with channels
    EqualiserName = "StormAudio"                               // Output equalizer name
};
```

### `ConversionOptionsUI`
UI-friendly options model for Blazor components:

```csharp
var uiOptions = new ConversionOptionsUI
{
    EqualiserName = "StormAudio",
    QType = QValueType.RBJ,
    CombineShared = false,
    IncludeParametricEQ = true,
    IncludeAllPass = true,
    ExcludeGainBlock = true,
    ExcludeDelayBlock = true
};
```

### `MsoConverter`
Main converter class:

```csharp
var converter = new MsoConverter(options);
var result = converter.Convert(msoFileContent);
```

### `ConversionResult`
Contains the conversion results:

```csharp
public class ConversionResult
{
    public Dictionary<string, string> ChannelFiles { get; set; }    // Generated channel files
    public string? SharedSubFile { get; set; }                     // Shared subwoofer file
    public int TotalFiltersProcessed { get; set; }                 // Statistics
    public int TotalFiltersExported { get; set; }
    public List<string> ProcessingLog { get; set; }                // Conversion log
}
```

## Basic Usage

### Console Application

```csharp
// Create options
var options = new ConversionOptions
{
    QType = "rbj",
    IncludedTypes = new List<string> { "Parametric EQ", "All-Pass" },
    CombineShared = false
};

// Create converter
var converter = new MsoConverter(options);

// Read MSO file
var msoContent = File.ReadAllText("mso-filters.txt");

// Convert
var result = converter.Convert(msoContent);

// Save results
foreach (var (fileName, content) in result.ChannelFiles)
{
    File.WriteAllText($"output/{fileName}", content);
}
```

### Blazor Component

```csharp
@inject MsoConversionService ConversionService

@code {
    private string msoContent = "";
    private ConversionOptionsUI options = new();
    
    private async Task ConvertMso()
    {
        var result = ConversionService.ConvertMso(msoContent, options);
        // Handle result...
    }
}
```

## Blazor Integration

### Service Registration

Add to your `Program.cs`:

```csharp
builder.Services.AddScoped<MsoConversionService>();
```

### Using the Service

```csharp
@inject MsoConversionService ConversionService

private async Task ConvertMsoFiles()
{
    // Validate content
    var validation = ConversionService.ValidateMsoContent(msoContent);
    if (!validation.IsValid)
    {
        // Show error message
        return;
    }
    
    // Get preview
    var preview = ConversionService.GetConversionPreview(msoContent, options);
    
    // Convert
    var result = ConversionService.ConvertMso(msoContent, options);
    
    // Download files
    var files = result.GetDownloadFiles();
    foreach (var file in files)
    {
        await DownloadFile(file.FileName, file.Content);
    }
}
```

## Conversion Examples

### Example 1: Basic Conversion
```csharp
var options = new ConversionOptions();  // Use defaults
var result = converter.Convert(msoContent);
```
**Output**: Separate files with Parametric EQ and All-Pass filters using RBJ Q values.

### Example 2: Classic Q Values Only
```csharp
var options = new ConversionOptions
{
    QType = "classic",
    IncludedTypes = new List<string> { "Parametric EQ" }
};
var result = converter.Convert(msoContent);
```
**Output**: Only Parametric EQ filters using Classic Q values.

### Example 3: Combined Output
```csharp
var options = new ConversionOptions
{
    CombineShared = true,
    EqualiserName = "Anthem AVM90"
};
var result = converter.Convert(msoContent);
```
**Output**: Each channel file contains shared subwoofer filters followed by channel-specific filters.

## File Download in Blazor

The `BlazorHelpers.cs` includes extension methods for easy file downloads:

```csharp
// Get all files ready for download
var downloadFiles = result.GetDownloadFiles();

// Download using JavaScript interop
foreach (var file in downloadFiles)
{
    var bytes = System.Text.Encoding.UTF8.GetBytes(file.Content);
    var base64 = Convert.ToBase64String(bytes);
    await JSRuntime.InvokeVoidAsync("downloadFile", file.FileName, base64, file.MimeType);
}
```

## Options Persistence

Save and load options using localStorage:

```csharp
// Save options
var json = ConversionService.SerializeOptions(options);
await JSRuntime.InvokeVoidAsync("localStorage.setItem", "msoOptions", json);

// Load options
var json = await JSRuntime.InvokeAsync<string>("localStorage.getItem", "msoOptions");
var options = ConversionService.DeserializeOptions(json);
```

## Testing

Run the console demo:

```bash
dotnet run
```

This will process the `sample-mso-filters.txt` file and generate output files in the `output_csharp` folder.

## Dependencies

- .NET 8.0+
- System.Text.Json (for Blazor helpers)

## Supported Filter Types

### Currently Supported
- **Parametric EQ (RBJ)**: Converted to Bell filters
- **All-Pass Second-Order**: Converted to All Pass filters

### Automatically Excluded (configurable)
- **Gain Block**: Not directly convertible to EQ format
- **Delay Block**: Not directly convertible to EQ format

## Output Format

The C# version produces identical output to the Python version:

### Parametric EQ Filters
```
Filter 1: ON Bell Fc 52.9284 Hz Gain -2.56499 dB Q 11.0387
```

### All-Pass Filters
```
Filter 9: ON All Pass Order 2 Fc 32.1576 Hz Gain 0 dB Q 0.500044
```

## Error Handling

The converter includes comprehensive error handling:

```csharp
var result = converter.Convert(msoContent);

// Check for errors in the processing log
if (result.ProcessingLog.Any(log => log.StartsWith("Error")))
{
    // Handle conversion errors
}
```

## Performance

The C# implementation is optimized for:
- Client-side execution in Blazor WASM
- Memory efficiency with large MSO files
- Fast regex-based parsing
- Minimal dependencies

## Compatibility

This C# implementation maintains 100% compatibility with the original Python version:
- Same input format support
- Identical output format
- All conversion options available
- Same filter type support
