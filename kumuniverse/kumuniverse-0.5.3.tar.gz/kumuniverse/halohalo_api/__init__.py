"""
Halohalo API Module for managing the Segmentation Platform.
"""

import requests
import json
import time
from pyspark.sql.functions import *


class HalohaloAPI:
    def __init__(self, env="dev", mongo_username=None, mongo_password=None):
        """
        Initializes Halohalo API.

        Args:
        - env (string): "dev" or "live", defaults to "dev" if neither
        - mongo_username (string): username to be used for database access to MongoDB Cluster
        - mongo_password (string): password to be used for database access to MongoDB Cluster
        """

        self.base_url = f"https://{env}-halohalo.kumuapi.com/v1"
        self.headers = {"Content-Type": "application/json"}

        if env == "live":
            self.cluster = "live-segp.q0znb.mongodb.net"
            mongo_cluster = self.cluster
        else:
            self.cluster = "dev-segp-dedicated.q0znb.mongodb.net"
            mongo_cluster = self.cluster

        self.database = "segmentation_platform"
        mongo_database = self.database

        self.mongo_username = mongo_username
        self.mongo_password = mongo_password
        self.uri = f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster}/{mongo_database}?retryWrites=true&w=majority"

    def get_user_segments(self, body):
        """
        Retrieves the list of segments that the target user is a part of

        Parameters
        ----------
        body : Python object, required
            Takes in `user_id` and `use_case` attributes (default is None)

            Example :
                {
                    "user_id": "t7dHZ5KrXqpWLC1i"
                }

        Returns
        -------
        Python object
        """
        try:
            user_id = body["user_id"]
        except Exception as e:
            raise Exception(
                f"ERROR: Could not parse `user_id` from the provided input body {body}, with error: {str(e)}"
            )

        get_user_segments_url = self.base_url + "/segments/users/" + user_id
        try:
            res = requests.get(url=get_user_segments_url, headers=self.headers)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as errh:
            raise ("HTTP ERROR:", errh)
        except requests.exceptions.ConnectionError as errc:
            raise ("CONNECTION ERROR:", errc)
        except requests.exceptions.Timeout as errt:
            raise ("TIMEOUT ERROR:", errt)
        except requests.exceptions.RequestException as err:
            raise ("REQEUST ERROR:", err)

    def update_segment(self, input_df, target_collection, target_segment):
        """
        Mirrors the segment collection against the input list of users provided in input_df.

        Args:
        - input_df (Spark DataFrame): Dataframe to be ingested into the target segment.
          Should contain the columns `user_id` and `segment_name`
        - target_collection (string): Target collection to ingest input_df.
          This should be an existing collection within the MongoDB cluster or else this will return an error
        - target_segment (string): Target segment that input_df should update.
          Will return an error if this is not an existing segment.
        """

        try:
            # Input Handling
            pass

            source_df = (
                input_df.select(col("user_id"), col("segment_name"))
                .withColumnRenamed("user_id", "source_user_id")
                .withColumnRenamed("segment_name", "source_segment_name")
                .filter(col("source_segment_name") == target_segment)
            )
            print(
                f"Finished formatting input_df with dimensions: {source_df.count()}, {len(source_df.columns)}"
            )
            display(source_df)

            existing_df = (
                spark.read.format("com.mongodb.spark.sql.DefaultSource")
                .option("uri", self.uri)
                .option("collection", target_collection)
                .load()
                .filter(col("segment_name") == target_segment)
                .select(
                    col("_id"),
                    col("user_id"),
                    col("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
            )
            print(
                f"Pulled the existing segment from collection with dimensions: {existing_df.count()}, {len(existing_df.columns)}"
            )
            display(existing_df)

            if int(existing_df.count()) == 0:
                raise Exception(
                    f"Target segment {target_segment} does not exist in {target_collection}"
                )

            join_conds = [
                existing_df.user_id == source_df.source_user_id,
                existing_df.segment_name == source_df.source_segment_name,
            ]

            insert_df = (
                source_df.join(existing_df, join_conds, "left_anti")
                .withColumn("created_at", lit(int(time.time())))
                .withColumn("updated_at", lit(int(time.time())))
                .withColumn("is_member", lit(True))
                .select(
                    col("source_user_id").alias("user_id"),
                    col("source_segment_name").alias("segment_name"),
                    col("is_member"),
                    col("created_at"),
                    col("updated_at"),
                )
            )
            print(
                f"The following {insert_df.count()} users will be inserted into {target_segment}"
            )
            display(insert_df)

            update_add_df = (
                source_df.join(existing_df, join_conds, "inner")
                .filter(col("is_member") == False)
                .drop(col("is_member"))
                .withColumn("is_member", lit(True))
                .select(
                    col("_id"),
                    col("source_user_id").alias("user_id"),
                    col("source_segment_name").alias("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
                .withColumn("updated_at", lit(int(time.time())))
            )
            print(
                f"The following {update_add_df.count()} existing users will be updated to ACTIVE membership in {target_segment}"
            )
            display(update_add_df)

            update_remove_df = (
                existing_df.join(source_df, join_conds, "left_anti")
                .filter(col("is_member") == True)
                .drop(col("is_member"))
                .withColumn("is_member", lit(False))
                .select(
                    col("_id"),
                    col("user_id"),
                    col("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
                .withColumn("updated_at", lit(int(time.time())))
            )
            print(
                f"The following {update_remove_df.count()} existing users will be updated to INACTIVE membership in {target_segment}"
            )
            display(update_remove_df)

            total_users = (
                int(insert_df.count())
                + int(update_add_df.count())
                + int(update_remove_df.count())
            )
            print("-----" * 10)
            print("PRE-OPERATION SUMMARY:")
            print(f"{insert_df.count()} users will be INSERTED into {target_segment}")
            print(
                f"{update_add_df.count()} users will be ACTIVATED (from being deactive) into {target_segment}"
            )
            print(
                f"{update_remove_df.count()} users will be DEACTIVATED (from being active) from {target_segment}"
            )
            print(
                f"Total of {total_users} will be processed. Proceeding with the update operations to {target_segment} in {self.cluster} / {self.database}"
            )
            print("-----" * 10)

            try:
                temp_df = insert_df
                res = (
                    insert_df.withColumn("updated_at", lit(int(time.time())))
                    .write.format("mongo")
                    .option("uri", self.uri)
                    .mode("append")
                    .option("database", self.database)
                    .option("collection", target_collection)
                    .save()
                )

                print(
                    f"Successfully added {temp_df.count()} users into the target segment: {target_segment}"
                )
                display(temp_df.select(col("user_id")))

            except Exception as e:
                print(
                    f"Failed to add {temp_df.count()} users into the target segment: {target_segment}, with error: {str(e)}"
                )
                display(temp_df.select(col("user_id")))

            try:
                temp_df = update_add_df
                res = (
                    update_add_df.withColumn("updated_at", lit(int(time.time())))
                    .write.format("mongo")
                    .option("uri", self.uri)
                    .mode("append")
                    .option("database", self.database)
                    .option("collection", target_collection)
                    .save()
                )

                print(
                    f"Successfully updated status of {temp_df.count()} users to ACTIVE in the target segment: {target_segment}"
                )
                display(temp_df.select(col("user_id")))

            except Exception as e:
                print(
                    f"Failed to update the status of {temp_df.count()} users to ACTIVE in the target segment: {target_segment}, with error: {str(e)}"
                )
                display(temp_df.select(col("user_id")))

            try:
                temp_df = update_remove_df
                res = (
                    update_remove_df.withColumn("updated_at", lit(int(time.time())))
                    .write.format("mongo")
                    .option("uri", self.uri)
                    .mode("append")
                    .option("database", self.database)
                    .option("collection", target_collection)
                    .save()
                )

                print(
                    f"Successfully updated status of {temp_df.count()} users to INACTIVE in the target segment: {target_segment}"
                )
                display(temp_df.select(col("user_id")))

            except Exception as e:
                print(
                    f"Failed to update the status of {temp_df.count()} users to INACTIVE in the target segment: {target_segment}, with error: {str(e)}"
                )
                display(temp_df.select(col("user_id")))

            res = {
                "status": 200,
                "response": f"SUCCESS: Finished processing {total_users} users into {target_segment}",
            }
            print(res["response"])

        except Exception as e:
            res = {
                "status": 400,
                "response": f"FAILED: Could not complete the operation due to error: {str(e)}",
            }
            print(res["response"])

        return res

    def remove_users_from_segment(self, input_df, target_collection, target_segment):
        """
        This method specifically takes the input list of users and removes them from the existing segment.

        Args:
        - input_df (Spark DataFrame): Dataframe to be ingested into the target segment.
          Should contain the columns `user_id` and `segment_name`
        - target_collection (string): Target collection to ingest input_df.
          This should be an existing collection within the MongoDB cluster or else this will return an error
        - target_segment (string): Target segment that input_df should update.
          Will return an error if this is not an existing segment.
        """

        try:
            # Input Handling
            pass

            source_df = (
                input_df.select(col("user_id"), col("segment_name"))
                .withColumnRenamed("user_id", "source_user_id")
                .withColumnRenamed("segment_name", "source_segment_name")
                .filter(col("source_segment_name") == target_segment)
            )
            print(
                f"Finished formatting input_df with dimensions: {source_df.count()}, {len(source_df.columns)}"
            )
            display(source_df)

            existing_df = (
                spark.read.format("com.mongodb.spark.sql.DefaultSource")
                .option("uri", self.uri)
                .option("collection", target_collection)
                .load()
                .filter(col("segment_name") == target_segment)
                .select(
                    col("_id"),
                    col("user_id"),
                    col("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
            )
            print(
                f"Pulled the existing segment from collection with dimensions: {existing_df.count()}, {len(existing_df.columns)}"
            )
            display(existing_df)

            if int(existing_df.count()) == 0:
                raise Exception(
                    f"Target segment {target_segment} does not exist in {target_collection}"
                )

            join_conds = [
                existing_df.user_id == source_df.source_user_id,
                existing_df.segment_name == source_df.source_segment_name,
            ]

            update_remove_df = (
                source_df.join(existing_df, join_conds, "inner")
                .filter(col("is_member") == True)
                .drop(col("is_member"))
                .withColumn("is_member", lit(False))
                .select(
                    col("_id"),
                    col("source_user_id").alias("user_id"),
                    col("source_segment_name").alias("segment_name"),
                    col("is_member"),
                    col("created_at"),
                )
                .withColumn("updated_at", lit(int(time.time())))
            )
            print(
                f"The following {update_remove_df.count()} existing users will be updated to ACTIVE membership in {target_segment}"
            )
            display(update_remove_df)

            total_users = int(update_remove_df.count())
            print("-----" * 10)
            print("PRE-OPERATION SUMMARY:")
            print(
                f"{update_remove_df.count()} users will be DEACTIVATED (from being active) from {target_segment}"
            )
            print(
                f"Total of {total_users} will be processed. Proceeding with the update operations to {target_segment} in {self.cluster} / {self.database}"
            )
            print("-----" * 10)

            try:
                temp_df = update_remove_df
                res = (
                    update_remove_df.withColumn("updated_at", lit(int(time.time())))
                    .write.format("mongo")
                    .option("uri", self.uri)
                    .mode("append")
                    .option("database", self.database)
                    .option("collection", target_collection)
                    .save()
                )

                print(
                    f"Successfully updated status of {temp_df.count()} users to INACTIVE in the target segment: {target_segment}"
                )
                display(temp_df.select(col("user_id")))

            except Exception as e:
                print(
                    f"Failed to update the status of {temp_df.count()} users to INACTIVE in the target segment: {target_segment}, with error: {str(e)}"
                )
                display(temp_df.select(col("user_id")))

            res = {
                "status": 200,
                "response": f"SUCCESS: Finished processing {total_users} users into {target_segment}",
            }
            print(res["response"])

        except Exception as e:
            res = {
                "status": 400,
                "response": f"FAILED: Could not complete the operation due to error: {str(e)}",
            }
            print(res["response"])

        return res
