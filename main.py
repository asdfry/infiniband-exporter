import re
import time
import socket

from glob import glob
from prometheus_client import start_http_server, Gauge


if __name__ == "__main__":
    start_http_server(8000)

    metric = {
        "port_xmit_data": Gauge(
            "infiniband_xmit_data_per_second",
            "Transmitted data (bytes)",
            ["hostname", "hca", "kubernetes_name"],
        ),
        "port_xmit_packets": Gauge(
            "infiniband_xmit_packets_per_second",
            "Number of transmitted packets",
            ["hostname", "hca", "kubernetes_name"],
        ),
        "port_rcv_data": Gauge(
            "infiniband_rcv_data_per_second",
            "Received data (bytes)",
            ["hostname", "hca", "kubernetes_name"],
        ),
        "port_rcv_packets": Gauge(
            "infiniband_rcv_packets_per_second",
            "Number of received packets",
            ["hostname", "hca", "kubernetes_name"],
        ),
    }

    paths = [i for i in glob("/sys/class/infiniband/mlx*") if re.search(r"mlx\d_\d+", i)]
    cnt_names = ["port_xmit_data", "port_xmit_packets", "port_rcv_data", "port_rcv_packets"]
    last_cnt = {i.split("/")[-1]: {} for i in paths}
    hostname = socket.gethostname()

    for path in paths:
        hca = path.split("/")[-1]
        for cnt_name in cnt_names:
            with open(f"{path}/ports/1/counters/{cnt_name}", "r") as f:
                cnt = int(f.read().strip())
                last_cnt[hca][cnt_name] = cnt

    while True:
        start_time = time.time()

        for path in paths:
            hca = path.split("/")[-1]
            for cnt_name in cnt_names:
                with open(f"{path}/ports/1/counters/{cnt_name}", "r") as f:
                    cnt = int(f.read().strip())
                    metric[cnt_name].labels(
                        hostname,
                        hca,
                        "infiniband-exporter",
                    ).set(cnt - last_cnt[hca][cnt_name])
                    last_cnt[hca][cnt_name] = cnt

        sec = 1 - (time.time() - start_time)
        if sec > 0:
            time.sleep(sec)
        else:
            time.sleep(sec)
