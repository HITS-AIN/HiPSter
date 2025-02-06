# Detail Page on demand

As a first application we plot the original and the reconstructed Gaia XP spectra.

Create container:
```
podman build -t gaia-plot-on-demand -f Containerfile .
```

Run container:
```
podman run -p 8080:8080 gaia-plot-on-demand
```

Test url request:
```
http://localhost:8080/?index=38655544960
```
