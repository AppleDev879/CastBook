source_file_name = "./res/imdb-roles.txt"
destination_file_name = "./res/roles.csv"

# Open the source file in read mode
with open(source_file_name, "r") as source_file:
    # Read the contents of the source file
    source_contents = source_file.read()

    # Open the destination file in append mode
    with open(destination_file_name, "a") as destination_file:
        # Append the contents of the source file to the destination file
        destination_file.write('\n' + source_contents)

# The contents of the source file have been appended to the destination file
print(f"Appended {source_file_name} to {destination_file_name}")
