if __name__ == "__main__":
    from utils.amber_utils import Amber

    amber_obj = Amber()
    results = amber_obj.get_usage()
    amber_obj.unwrap_usage(results)
