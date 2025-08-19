using System;
using System.IO;
using MsoRewConverter;

namespace MsoRewConverter.Demo
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("MSO to REW Converter - C# Demo");
            Console.WriteLine("======================================");

            // Example usage with default options
            var options = new ConversionOptions
            {
                QType = "rbj",
                IncludedTypes = new List<string> { "Parametric EQ", "All-Pass" },
                ExcludedTypes = new List<string> { "Gain Block", "Delay Block" },
                CombineShared = false,
                EqualiserName = "StormAudio"
            };

            var converter = new MsoConverter(options);

            // Check if sample file exists
            var sampleFile = "../sample-mso-filters.txt";
            if (!File.Exists(sampleFile))
            {
                Console.WriteLine($"Error: Sample file '{sampleFile}' not found.");
                Console.WriteLine("Please ensure the sample MSO file is in the current directory.");
                return;
            }

            try
            {
                // Read the MSO file content
                var msoContent = File.ReadAllText(sampleFile);
                
                Console.WriteLine($"Processing MSO file: {sampleFile}");
                Console.WriteLine();

                // Convert the content
                var result = converter.Convert(msoContent);

                // Display processing log
                foreach (var logEntry in result.ProcessingLog)
                {
                    Console.WriteLine(logEntry);
                }

                Console.WriteLine();
                Console.WriteLine("Generated Files:");
                Console.WriteLine("================");

                // Save the generated files
                var outputDir = "output_csharp";
                Directory.CreateDirectory(outputDir);

                foreach (var (fileName, content) in result.ChannelFiles)
                {
                    var filePath = Path.Combine(outputDir, fileName);
                    File.WriteAllText(filePath, content);
                    Console.WriteLine($"✓ {fileName} ({content.Split('\n').Length - 1} lines)");
                }

                if (!string.IsNullOrEmpty(result.SharedSubFile))
                {
                    var sharedFilePath = Path.Combine(outputDir, "shared_sub_filters.txt");
                    File.WriteAllText(sharedFilePath, result.SharedSubFile);
                    Console.WriteLine($"✓ shared_sub_filters.txt ({result.SharedSubFile.Split('\n').Length - 1} lines)");
                }

                Console.WriteLine();
                Console.WriteLine($"Files saved to: {Path.GetFullPath(outputDir)}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }

            Console.WriteLine();
        }
    }
}

// Example of how to use different options in Blazor
public static class ConverterExamples
{
    /// <summary>
    /// Example: Convert with classic Q values
    /// </summary>
    public static ConversionResult ConvertWithClassicQ(string msoContent)
    {
        var options = new ConversionOptions
        {
            QType = "classic",
            IncludedTypes = new List<string> { "Parametric EQ" },
            ExcludedTypes = new List<string> { "Gain Block", "Delay Block", "All-Pass" },
            CombineShared = false,
            EqualiserName = "MyProcessor"
        };

        var converter = new MsoConverter(options);
        return converter.Convert(msoContent);
    }

    /// <summary>
    /// Example: Convert with combined shared filters
    /// </summary>
    public static ConversionResult ConvertWithCombinedShared(string msoContent)
    {
        var options = new ConversionOptions
        {
            QType = "rbj",
            IncludedTypes = new List<string> { "Parametric EQ" },
            ExcludedTypes = new List<string> { "Gain Block", "Delay Block", "All-Pass" },
            CombineShared = false,
            EqualiserName = "Processor X"
        };

        var converter = new MsoConverter(options);
        return converter.Convert(msoContent);
    }

    /// <summary>
    /// Example: Convert only Parametric EQ filters
    /// </summary>
    public static ConversionResult ConvertParametricEqOnly(string msoContent)
    {
        var options = new ConversionOptions
        {
            QType = "rbj",
            IncludedTypes = new List<string> { "Parametric EQ", "All-Pass" },
            ExcludedTypes = new List<string> { "Gain Block", "Delay Block" },
            CombineShared = true,
            EqualiserName = "StormAudio"
        };

        var converter = new MsoConverter(options);
        return converter.Convert(msoContent);
    }
}
