MERGE
    `{project_id}.{target_dataset}.{target_table}` T
USING
  ({source_statement}) AS S
ON
(T.{target_partition_field} >= '{oldest_target_partition}')
  AND {merge_keys}
  WHEN MATCHED THEN UPDATE SET {update_statements}
  WHEN NOT MATCHED
  THEN
INSERT
  ({columns})
VALUES
  ({columns});
