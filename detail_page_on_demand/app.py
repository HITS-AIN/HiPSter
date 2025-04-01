import os

import matplotlib.pyplot as plt
import numpy as np
import onnxruntime as ort
import streamlit as st
from gaiaxpy import calibrate


def file_selector(folder_path: str) -> str:
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox("ONNX model", filenames)
    return os.path.join(folder_path, selected_filename)


st.title("HiPSter: Gaia XP DR3")

model_path = file_selector("/home/doserbd/gaia/")
# st.write(f"You selected {model_path}")

# source_index = 38655544960
source_index = st.query_params["index"]

calibrated_spectrum, sampling = calibrate(
    [source_index], sampling=np.arange(336, 1021, 2), save_file=False
)

flux = calibrated_spectrum["flux"][0].astype(np.float32).reshape(-1, 1, 343)
flux_error = calibrated_spectrum["flux_error"][0].astype(np.float32).reshape(-1, 1, 343)
for i, (flux_data, flux_error) in enumerate(zip(flux, flux_error)):
    flux_min = flux_data.min()
    flux_max = flux_data.max()
    flux[i] = (flux_data - flux_min) / (flux_max - flux_min)
    flux_error[i] = flux_error / (flux_max - flux_min)

encoder = ort.InferenceSession(os.path.join(model_path, "encoder.onnx"))
decoder = ort.InferenceSession(os.path.join(model_path, "decoder.onnx"))

latent_position = encoder.run(None, {"x": flux})[0]
recon = decoder.run(None, {"x": latent_position})[0]
mse_loss = np.mean((flux - recon) ** 2)
nll_loss = np.nan

st.write(f"MSE loss: {mse_loss:.8f}")
st.write(f"NLL loss: {nll_loss:.8f}")
st.write(f"Source index: {source_index}")

fig, ax = plt.subplots()
ax.plot(sampling, flux[0][0], label="Original", alpha=0.5, color="orange")
ax.plot(sampling, recon[0][0], label="Reconstructed", color="blue")
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Normalized flux")
ax.legend()

ax.fill_between(
    sampling,
    flux[0][0] - flux_error[0][0],
    flux[0][0] + flux_error[0][0],
    alpha=0.5,
    facecolor="orange",
)

st.pyplot(fig)
