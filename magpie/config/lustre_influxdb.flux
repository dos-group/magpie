start = _start
stop = _end
// cache ratio
cache_ratio = from(bucket: "lustre")
  |> range(start: start, stop: stop)
  |> filter(fn: (r) => r["_measurement"] == "lustre")
  |> filter(fn: (r) => r["_field"] == "cache_hit" or r["_field"] == "cache_access")
  |> keep(columns: ["_field", "_value", "_time"])
  |> aggregateWindow(every: 1s, fn: sum, createEmpty: true)
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({
     r with cache_hit_ratio: float(v: r.cache_hit) / float(v: r.cache_access)
  }))
  |>mean(column:"cache_hit_ratio")
  |> keep(columns: ["_stop", "cache_hit_ratio"])

// lustre fs common statistics (cur_dirty_bytes, cur_grant_bytes, ...)
fs_common_stats = from(bucket: "lustre")
  |> range(start: start, stop: stop)
  |> filter(fn: (r) => r["_measurement"] == "lustre"  or r["_measurement"] == "cpu" or r["_measurement"] == "mem")
  |> filter(fn: (r) => r["_field"] == "cur_dirty_bytes" or r["_field"] == "cur_grant_bytes" or r["_field"] == "read_rpcs_in_flight" or r["_field"] == "write_rpcs_in_flight" or r["_field"] == "pending_read_pages" or r["_field"] == "pending_write_pages" or
                        r["_field"] == "usage_iowait" or r["_field"] == "usage_idle" or r["_field"] == "used_percent")
  |> keep(columns: ["_field", "_value", "_time"])
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
  |> mean()
  |> pivot(
    rowKey:["_stop"],
    columnKey: ["_field"],
    valueColumn: "_value"
  )

// lustre derivative statistics (e.g., read_bytes rate, ...)
fs_rates_stats = from(bucket: "lustre")
  |> range(start: start, stop: stop)
  |> filter(fn: (r) => r["_measurement"] == "lustre")
  |> filter(fn: (r) => r["_field"] == "read_calls" or r["_field"] == "read_bytes" or r["_field"] == "write_bytes" or r["_field"] == "write_calls")
  |> derivative(unit: 1s, nonNegative: false)
  |> keep(columns: ["_field", "_value", "_time"])
  |> aggregateWindow(every: 1s, fn: sum, createEmpty: true)
  |> mean()
    |> pivot(
    rowKey:["_stop"],
    columnKey: ["_field"],
    valueColumn: "_value"
  )
  |> keep(columns: [ "_stop", "read_bytes","read_calls","write_bytes","write_calls"])

// ram and cpu

// cache_ratio
// fs_rates_stats
// fs_common_stats
c = join(
    tables: {cache_ratio, fs_rates_stats},
    on: ["_stop"]
  )
join(tables: {c, fs_common_stats}, on:  ["_stop"])