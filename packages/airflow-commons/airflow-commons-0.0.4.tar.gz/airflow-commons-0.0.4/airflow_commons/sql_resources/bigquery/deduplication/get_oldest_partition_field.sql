SELECT
  MIN({target_partition_field}) AS oldest_value
FROM
  `{project_id}.{target_dataset}.{target_table}`
INNER JOIN (
  SELECT
    {primary_key_list}
  FROM
    `{project_id}.{source_dataset}.{source_table}`
  WHERE
    {source_partition_field} BETWEEN '{start_date}'
    AND '{end_date}'
  GROUP BY
    {primary_key_list} )
USING
  ({primary_key_list});