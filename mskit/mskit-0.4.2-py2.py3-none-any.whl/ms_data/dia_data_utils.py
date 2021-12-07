import pandas as pd

__all__ = ['extract_dia_window_mzml']


def extract_dia_window_mzml(
        mzml_file,
        cut_overlap_at_half: bool = False,
        half_overlap_as_margin: bool = False,
        columns=('lower_offset', 'upper_offset', 'margin'),
        max_iter_spec_num: int = 150,
        sort: bool = True,
        drop_duplicates: bool = True,
) -> pd.DataFrame:
    try:
        import pymzml
        dia_windows = []
        start_record = False
        with pymzml.run.Reader(mzml_file) as mzml:
            for idx, spec in enumerate(mzml):
                if spec.ms_level == 1:
                    if start_record:
                        used_cols = columns[:2]
                        window_df = pd.DataFrame(dia_windows, columns=used_cols)
                        if drop_duplicates:
                            window_df = window_df.drop_duplicates(used_cols)
                        if sort:
                            window_df = window_df.sort_values(list(used_cols))
                        return window_df
                    else:
                        start_record = True
                elif spec.ms_level == 2:
                    if start_record:
                        dia_windows.append((
                            spec.selected_precursors[0]['mz'] - spec['MS:1000828'],
                            spec.selected_precursors[0]['mz'] + spec['MS:1000829']
                        ))
                else:
                    pass  # OR Raise
                if idx > max_iter_spec_num:
                    if start_record:
                        raise ValueError(f'Iterate mzml file for {max_iter_spec_num} spectra but no further MS1 appear')
                    else:
                        raise ValueError(f'Iterate mzml file for {max_iter_spec_num} spectra but no MS1 spectrum appear')
    except ModuleNotFoundError:
        raise ModuleNotFoundError('pymzml is not installed.')
