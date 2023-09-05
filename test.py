import tempfile

named_file = tempfile.TemporaryFile(
    dir='./'
)
 
print('File created in the cwd')
print(named_file.name)
 
# Closing the file
named_file.close()