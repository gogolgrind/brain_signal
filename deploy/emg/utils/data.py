import pandas as pd


def read_events_edf(filename):
    if filename[-4:] != ".edf":
        raise ValueError("Incorrect extension of file")

    timestamps = []
    names = []
    with open(filename, "rb") as f:
        data = f.read()
        try:
            header_size = int(data[184:191])
            # data_records_num = int(data[236:243])
        except ValueError:
            raise ValueError("Corrupted structure of edf file!")

        real_data = data[header_size:]
        if len(real_data) == 0:
            raise ValueError("Corrupted structure of edf file!")

        data_of_interest = real_data.split(b"+")[2::2]
        for doi in data_of_interest:
            time, name, rest = doi.split(b"\x14")
            print(int(str(time)[2:-1].split(".")[0]))
            timestamps.append(int(str(time)[2:-1].split(".")[0]))
            names.append(str(name)[2:-1])

    return pd.DataFrame(data=names, index=timestamps)