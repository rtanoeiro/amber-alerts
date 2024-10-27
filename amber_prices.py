if __name__ == "__main__":
    from utils.amber_utils import Amber
    from utils.postgres import insert_into_usage_table

    amber_obj = Amber()
    results = amber_obj.get_usage()
    energy_list = amber_obj.unwrap_usage(results)
    insert_into_usage_table(energy_list)
