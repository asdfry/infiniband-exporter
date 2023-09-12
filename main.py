import re
import time

from glob import glob
from pprint import pprint
from prometheus_client import start_http_server, Gauge


if __name__ == "__main__":
    start_http_server(8000)

    paths = [i for i in glob("/sys/class/infiniband/mlx*") if re.search(r"mlx\d_\d+", i)]
    cnt_names = ["port_xmit_data", "port_xmit_packets", "port_rcv_data", "port_rcv_packets"]
    last_cnt = {i.split("/")[-1]: {} for i in paths}

    for path in paths:
        hca = path.split("/")[-1]
        for cnt_name in cnt_names:
            with open(f"{path}/ports/1/counters/{cnt_name}", "r") as f:
                cnt = int(f.read().strip())
                last_cnt[hca][cnt_name] = {}
                last_cnt[hca][cnt_name]["metric"] = Gauge(f"{hca}_{cnt_name}", f"HCA: {hca}, Counter: {cnt_name}")
                last_cnt[hca][cnt_name]["value"] = cnt

    while True:
        start_time = time.time()

        for path in paths:
            hca = path.split("/")[-1]
            for cnt_name in cnt_names:
                with open(f"{path}/ports/1/counters/{cnt_name}", "r") as f:
                    cnt = int(f.read().strip())
                    last_cnt[hca][cnt_name]["metric"].set(cnt - last_cnt[hca][cnt_name]["value"])
                    last_cnt[hca][cnt_name]["value"] = cnt

        sec = 1 - (time.time() - start_time)
        if sec < 0:
            time.sleep(1)
        else:
            time.sleep(sec)
