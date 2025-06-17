import base64
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import onnxruntime as ort
from gaiaxpy import calibrate


class PlotRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        figsize_in_pixel = (1600, 1200)
        self.dpi = 200
        self.figsize = (
            float(figsize_in_pixel[0]) / self.dpi,
            float(figsize_in_pixel[1]) / self.dpi,
        )
        self.legend = True
        self.encoder = ort.InferenceSession("./gaia-v1/encoder.onnx")
        self.decoder = ort.InferenceSession("./gaia-v1/decoder.onnx")
        super().__init__(*args, **kwargs)

    def __generate_plot(self, index) -> str:
        try:
            calibrated_spectrum, _ = calibrate([index], sampling=np.arange(336, 1021, 2), save_file=False)
        except ValueError:
            return f"""<html><body><h1>Error: No continuous raw data found for the given
                   source index {index}.</h1></body></html>"""

        # Add dummy entry to the end of the flux and flux_error columns to make it divisible by 4
        calibrated_spectrum["flux"] = calibrated_spectrum["flux"].apply(lambda x: np.append(x, x[-1]))

        flux = calibrated_spectrum["flux"][0].astype(np.float32).reshape(-1, 1, 344)
        for i, x in enumerate(flux):
            flux[i] = (x - x.min()) / (x.max() - x.min())

        latent_position = self.encoder.run(None, {"l_x_": flux})[0]
        recon = self.decoder.run(None, {"l_x_": latent_position})[0]
        loss = np.mean((flux - recon) ** 2)

        plt.figure(figsize=self.figsize, dpi=self.dpi)
        plt.plot(flux[0][0], label="Original")
        plt.plot(recon[0][0], label="Reconstructed")
        if self.legend:
            plt.legend(loc="upper right")
        with BytesIO() as buf:
            plt.savefig(buf, format="jpg")
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode()
        plt.close()
        return (
            f"""<html><body><h1>Plot for Gaia XP source {index}</h1>"""
            f"""<p>Loss: {loss}</p>"""
            f"""<img src="data:image/jpg;base64,{img_base64}" /></body></html>"""
        )

    def do_GET(self):
        args = urllib.parse.parse_qs(self.path[2:])
        args = {i: args[i][0] for i in args}

        if "index" not in args:
            html = """<html><body><h1>Error: No index provided</h1></body></html>"""
        else:
            html = self.__generate_plot(args["index"])

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


def run(server_class=HTTPServer, handler_class=PlotRequestHandler, port=8080):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
