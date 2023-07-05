import sys
import os
from awsglue.context import GlueContext
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, split, lower
from pyspark.sql.functions import input_file_name, split

# Create a SparkContext
sc = SparkContext()
glueContext = GlueContext(sc)

# Get the input arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

# Create a SparkSession
spark = glueContext.spark_session

# Read the input JSON files from S3
input_dynamic_frame = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": ["s3://verusen-poc"], "recurse": True},
    format="json",
)

# Infer the schema from the input data
input_dataframe = input_dynamic_frame.toDF()
input_dataframe = input_dataframe.withColumn("file_name", input_file_name())
input_dataframe = input_dataframe.withColumn(
    "folder_name", split(input_dataframe["file_name"], "/")[-2]
)

# Define the output directory for CSV files
output_directory = "s3://verusen-poc/csv/"

# Transform and write each input DataFrame to CSV
input_files = input_dataframe.select("file_name").distinct().collect()
for row in input_files:
    file_name = row["file_name"]
    output_path = os.path.join(
        output_directory,
        os.path.splitext(file_name)[0] + ".csv",
    )
    input_dataframe.filter(input_dataframe.file_name == file_name).coalesce(
        1
    ).write.csv(output_path, header=True, mode="overwrite")

# Define the PostgreSQL connection properties
postgres_properties = {
    "driver": "org.postgresql.Driver",
    "url": "jdbc:postgresql://verusen-poc-db.csrzgzb20byt.sa-east-1.rds.amazonaws.com:5432/verusen",
    "user": "verusen",
    "password": "verusen123",
}

# Write each input DataFrame to a separate PostgreSQL RDS database table
input_dataframe.write.jdbc(
    url=postgres_properties["url"],
    table=input_dataframe["folder_name"] + "." + input_dataframe["file_name"],
    mode="append",
    properties=postgres_properties,
    createTableColumnTypes={"CAS #": "TEXT PRIMARY KEY"},
)

# Extract the INDUSTRY, CLASS, and FUNCTIONS columns
columns_to_extract = ["INDUSTRY", "CLASS", "FUNCTIONS"]
extracted_dataframe = input_dataframe.select(columns_to_extract)

# Write the extracted data to separate tables in PostgreSQL
schema_name = (
    input_dataframe["folder_name"].unique().head()
)  # Get the unique schema name
for column in columns_to_extract:
    table_name = column.lower()
    full_table_name = (
        schema_name + "." + table_name
    )  # Combine schema name and table name
    column_dataframe = extracted_dataframe.select(column)
    column_dataframe.write.jdbc(
        url=postgres_properties["url"],
        table=full_table_name,
        mode="append",
        properties=postgres_properties,
        options={
            "createTableColumnTypes": "id BIGSERIAL PRIMARY KEY, " + column + " TEXT"
        },
    )
