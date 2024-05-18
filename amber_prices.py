from utils.amber_utils import AmberSummary

amber_obj = AmberSummary()
energy_dataframe = amber_obj.create_energy_dataframe()
energy_dataframe =  amber_obj.basic_formatting(energy_dataframe=energy_dataframe)
amber_obj.summarize_energy(summary_level='day', energy_dataframe=energy_dataframe)
amber_obj.summarize_energy(summary_level='month', energy_dataframe=energy_dataframe)
amber_obj.summarize_energy(summary_level='year', energy_dataframe=energy_dataframe)
