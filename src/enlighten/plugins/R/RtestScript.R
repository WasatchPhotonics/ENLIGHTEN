###############################################
#
#   Example R Script to be called from
#   Enlighten Plug in
#
#   Input:
#       spectra_output.csv = CSV file with three columns: 
#           wavelengths, wavenumbers, and intensities ('spectrum')
#
#   Output:
#       analysis_return.csv = CSV with key value pairs of results
#
###############################################


# needed for reading CSV, should be part of the standard install
library(utils)

# hard coded file names
inputFileName <- "spectrum_output.csv"
outputFileName <- "analysis_return.csv"

# say Hi first
print("Hello Script!")


print("Read Input")
print(paste("input:", inputFileName))

# read input
if (file.exists(inputFileName)) {
    spectrum <- read.csv(inputFileName, header = TRUE)
} else {
    stop("Input File not found... Stopping...")
}

print("Start Analysis...")

# do very difficult analysis
peakSignal <- max(spectrum$processed)
peakIndex <- which.max(spectrum$processed)
peakPosition <- spectrum$wavenumber[peakIndex]

# form output key value pairs
analysisResults <- list(Peak.Position = peakPosition,
                        Peak.Signal = peakSignal)

# turn into list running down
analysisOutput <- data.frame(Key = names(analysisResults),
                             Value = unlist(analysisResults))

print("...Analysis DONE!")

print("Write Results")
print(paste("output:", outputFileName))

# write to csv
write.table(analysisOutput, file = outputFileName, sep = ",",
            row.names = FALSE, col.names = FALSE)


# Say Bye
print("Bye Bye Script!")


