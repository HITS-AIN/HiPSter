import dask.dataframe as dd
import pyarrow as pa

ddf = dd.read_parquet(
    "/home/doserbd/data/gaia/xp_sampled_mean_spectrum/parquet/XpSampledMeanSpectrum_000000-003111.parquet"
)

schema = {
    "flux": pa.list_(pa.float32()),
    "flux_error": pa.list_(pa.float32()),
}

ddf.repartition(npartitions=1000).to_parquet(
    "tests/data/XpSampledMeanSpectrum",
    schema=schema,
    custom_metadata={"flux_shape": "(1, 344)"},
)
