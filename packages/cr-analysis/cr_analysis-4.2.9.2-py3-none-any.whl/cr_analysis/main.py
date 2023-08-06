"""
==========
Author: Tomoki WATANABE
Update: 01/03/2021
Version: 4.2.9.2
License: BSD License
Programing Language: Python3
==========
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import itertools
import json
from sklearn.metrics import r2_score
from statistics import mean, stdev
from scipy import stats

"""
def f_test(A, B):
    # 参考：https://qiita.com/suaaa7/items/745ac1ca0a8d6753cf60
    A_var = np.var(A, ddof=1)  # Aの不偏分散
    B_var = np.var(B, ddof=1)  # Bの不偏分散
    A_df = len(A) - 1  # Aの自由度
    B_df = len(B) - 1  # Bの自由度
    f = A_var / B_var  # F比の値
    one_sided_pval1 = st.f.cdf(f, A_df, B_df)  # 片側検定のp値 1
    one_sided_pval2 = st.f.sf(f, A_df, B_df)   # 片側検定のp値 2
    two_sided_pval = min(one_sided_pval1, one_sided_pval2) * 2  # 両側検定のp値

    print('F:       ', round(f, 3))
    print(f'p-value: {round(two_sided_pval, 3)}')
    if round(two_sided_pval, 3) > 0.05:
        print('この2群間は少なくとも「不」等分散でない -> Student T検定可')
        reslut = stats.ttest_rel(A, B)
        print(reslut)
        if reslut.pvalue < 0.05:
            print('2群間には差があると言える')
        else :
            print('2群間には差があるとは言え「ない」')
    else :
        print('この2群間は少なくとも等分散でない -> Student T検定「不」可')
"""

class visualizer:
    def __init__(
        self, 
        file_name, 
        common_setting,
        subtitle_and_color,
        file_path = "/content/"
        # compare_info
    ):

        # 96well positions 読み込み
        def well_positions_reader(file_name, file_location = file_path):
            # group_list = sorted(list(set(sum(positions.values.tolist(), []))))
            if os.path.exists(file_location + file_name):
                file_type = file_name.split(".")[-1]
                if file_type == "xlsx":
                    return pd.read_excel(file_location + file_name, usecols=[i for i in range(0, 13, 1)], index_col=0)[:8] #, group_list
                elif file_type == "csv":
                    return pd.read_csv(file_location + file_name, engine="python", encoding="utf-8_sig", index_col=0) # , group_list
                else :
                    print("Error : Please use xlsx or csv file.")
                    return None
            else :
                print("エラー：該当する名前の96well_position入力用ファイルが見つかりません。")
                return None

        # 測定結果読み込み
        def data_reader(file_name, file_location = file_path): 
            # LUMICEC出力データ読み込み
            def lumicec_reader(file_location, file_name):
                # if not file_name.split(".")[-1] == "xlsx":
                #     return print("エラー：Lumicecから取得したxlsx（エクセル）ファイルを指定してください。")
                index_rename_dict = {}
                for letter in ["A", "B", "C", "D", "E", "F", "G", "H"]:
                    for i in range(1, 13, 1):
                        index_rename_dict[letter + "列" + str(i)] = letter + (('0' + str(i)) if i <10 else str(i))
                try :
                    return pd.read_excel(
                                  file_location + "/" + file_name, 
                                  # engine="python", 
                                  # encoding="shift-jis", 
                                  # skiprows=2, 
                                  usecols=lambda x: x not in ['Time'], 
                                  sheet_name='plate1'
                                ).rename(columns=index_rename_dict)
                except Exception as e:
                    print("エラー：LUMICECデータの読み込みに失敗しました。\nシステムメッセージ：\n" + str(e))

            # ALOKA出力データ読み込み
            def aloka_reader(file_location, file_name):
                # if not file_name.split(".")[-1] == "csv":
                #    return print("エラー：Alokaから取得したcsvファイルを指定してください。")
                index_rename_dict = {}
                for letter in ["A", "B", "C", "D", "E", "F", "G", "H"]:
                    for i in range(1, 13, 1):
                        index_rename_dict[letter + "列" + str(i)] = letter + (('0' + str(i)) if i <10 else str(i))
                try :
                    return pd.read_csv(
                                  file_location + "/" + file_name, 
                                  engine="python", 
                                  encoding="shift-jis", 
                                  skiprows=2, 
                                  usecols=lambda x: x not in ['通番', '日付', '時刻', 'リピート回数']
                                ).rename(columns=index_rename_dict)
                except Exception as e:
                    print("エラー：ALOKAデータの読み込みに失敗しました。\nシステムメッセージ：\n" + str(e))
                    return None

            file_type = file_name.split(".")[-1]
            # print(file_type)
            if file_type == "csv":
                return aloka_reader(file_location, file_name)
            elif file_type == "xlsx":
                column_names = [
                                    "A01",
                                    "A02",
                                    "A03",
                                    "A04",
                                    "A05",
                                    "A06",
                                    "A07",
                                    "A08",
                                    "A09",
                                    "A10",
                                    "A11",
                                    "A12",
                                    "B01",
                                    "B02",
                                    "B03",
                                    "B04",
                                    "B05",
                                    "B06",
                                    "B07",
                                    "B08",
                                    "B09",
                                    "B10",
                                    "B11",
                                    "B12",
                                    "C01",
                                    "C02",
                                    "C03",
                                    "C04",
                                    "C05",
                                    "C06",
                                    "C07",
                                    "C08",
                                    "C09",
                                    "C10",
                                    "C11",
                                    "C12",
                                    "D01",
                                    "D02",
                                    "D03",
                                    "D04",
                                    "D05",
                                    "D06",
                                    "D07",
                                    "D08",
                                    "D09",
                                    "D10",
                                    "D11",
                                    "D12",
                                    "E01",
                                    "E02",
                                    "E03",
                                    "E04",
                                    "E05",
                                    "E06",
                                    "E07",
                                    "E08",
                                    "E09",
                                    "E10",
                                    "E11",
                                    "E12",
                                    "F01",
                                    "F02",
                                    "F03",
                                    "F04",
                                    "F05",
                                    "F06",
                                    "F07",
                                    "F08",
                                    "F09",
                                    "F10",
                                    "F11",
                                    "F12",
                                    "G01",
                                    "G02",
                                    "G03",
                                    "G04",
                                    "G05",
                                    "G06",
                                    "G07",
                                    "G08",
                                    "G09",
                                    "G10",
                                    "G11",
                                    "G12",
                                    "H01",
                                    "H02",
                                    "H03",
                                    "H04",
                                    "H05",
                                    "H06",
                                    "H07",
                                    "H08",
                                    "H09",
                                    "H10",
                                    "H11",
                                    "H12"
                                ]
                lumicec_data = lumicec_reader(file_location, file_name)
                return pd.DataFrame(
                    [lumicec_data[col_name] for col_name in column_names],
                    index = column_names,
                    columns = lumicec_data.index
                ).T
            else :
                print("Error : Please use csv or xlsx file.")
                return None

        def moving_avrg(moving_avrg_range, data):
            if moving_avrg_range < 12 or moving_avrg_range > 36:
                print("Error : moving_avrg_range should be 12 ~ 36!")
                return 
            if moving_avrg_range % 2 == 0:
                return pd.DataFrame(
                    [[value[int(moving_avrg_range/2 + i)]/(sum(value[i+1:moving_avrg_range+i])/(moving_avrg_range-1) + (value[i] + value[moving_avrg_range+i])/2) for i in range(0, len(value) - moving_avrg_range, 1)] for value in data.T.values],
                    index = data.columns.values,
                    columns = range(int(moving_avrg_range/2), len(data) - int(moving_avrg_range/2), 1)
                ).T
            else :
                return pd.DataFrame(
                    [[value[int((moving_avrg_range-1)/2 + i)]/(sum(value[i:moving_avrg_range+i])/(moving_avrg_range)) for i in range(0, len(value) - moving_avrg_range+1, 1)] for value in data.T.values],
                    index = data.columns.values,
                    columns = range(int(moving_avrg_range/2), len(data) - int(moving_avrg_range/2), 1)
                ).T

        def range_extraction(
            original_data,
            extraction_start, 
            extraction_end
            ):
            if extraction_end == 0:

                return original_data[extraction_start:]
            else :
                if extraction_start >= extraction_end:
                    print('Error : "extraction_end" should be more than "extraction_start".')
                    return None
                else :
                    return original_data[extraction_start:extraction_end + 1]

        def col_posi_linker(col_name):
            if col_name[1] == "0":
                return self.positions.at[col_name[0], col_name[2]]
            else :
                return self.positions.at[col_name[0], col_name[1:3]]

        def percentage_cal(data):
            new_data = pd.DataFrame(columns=data.columns.values)
            for col in data.columns.values:
                new_data[col] = data[col]/max(data[col])*100
            return new_data

        self.file_name = file_name
        self.common_setting = common_setting
        self.subtitle_and_color = subtitle_and_color
        self.positions = well_positions_reader(common_setting["96well_position_file"])
        # print('Row data')
        # print(data_reader(file_name))
        ranged_data = range_extraction(data_reader(file_name), common_setting["analysis_start"], common_setting["analysis_end"])
        # print('Ranged data')
        # print(ranged_data)

        types = list(set(itertools.chain.from_iterable(row for row in self.positions.values)))
        types_dict = dict(zip(types, [[] for _ in range(len(types))]))

        if common_setting["yaxis_percentage_switch"]:
            if common_setting["moving_avrg_range"]:
                plot_data = percentage_cal(moving_avrg(common_setting["moving_avrg_range"], ranged_data))
            else :
                plot_data = percentage_cal(ranged_data)
            self.Y_max = 100
        else :
            if common_setting["moving_avrg_range"]:
                plot_data = moving_avrg(common_setting["moving_avrg_range"], ranged_data)
            else :
                plot_data = ranged_data
            self.Y_max = -(-np.amax(np.amax(ranged_data))//1000)*1000

        self.plot_data = plot_data

        for key in plot_data.columns:
            types_dict[col_posi_linker(key)].append(plot_data[key])
        # del types_dict[0]
        self.types_dict = types_dict

        print("Welcome to chlamy bioluminescence visualizer!")


    def overview(self, graph_width = 4, graph_length = 4, col_number = 3):
        data_types_dict = self.types_dict
        # return self.plot_data
        # print(data_types_dict)
        plot_count : int = 1
        fig = plt.figure(figsize=(col_number*graph_width, -(-len(data_types_dict)//col_number)*graph_length))
        # fig.suptitle('Overview')
        for key, value in data_types_dict.items():
            ax =  fig.add_subplot(len(data_types_dict)//col_number+1, col_number, plot_count)
            for col in value:
                ax.plot(col.index, col, color=self.subtitle_and_color[key][0])
            plot_count : int = plot_count + 1

            n_rythm : int = int(-(-((len(value[0])-1)//(60/self.common_setting["sampling_period"]))//24))

            ax.set_title(f'{self.subtitle_and_color[key][1]} (No.{key}), {len(value)}well')
            ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm+1))
            ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm*4+1), minor=True)
            ax.set_xlabel(self.common_setting["x_axis_title"])
            if self.common_setting["yaxis_share_switch"]:
                ax.set_ylim(0, self.Y_max)
            ax.set_ylabel(self.common_setting["y_axis_title"])
            ax.grid(axis="both")

        fig.tight_layout()
        if self.common_setting["plot_save_switch"]: # == 1
            plt.savefig(self.common_setting["save_path"] + f"overview_{col_number}_col_plot.jpg")
        else :
            pass
        plt.show()


    # MTとWTとかの系統単位での比較
    def strain_compare(self, strain_compare_info={}, graph_width = 4, graph_length = 4, col_number = 2, cal_range=12, bar_range = (15, 30)):

        def peak_detection(col_data, cal_range):
            index_min = min(col_data.index)
            x = []
            # y = []
            # for i in range(int(cal_range/2), len(col_data)-int(cal_range/2), 1):
            for i in range(0 + self.common_setting['peak_detection_after'], len(col_data)-1, 1):
                if i-int(cal_range/2) < 0:
                    local_max = max(col_data[0:i+int(cal_range/2)+1])
                else :
                    local_max = max(col_data[i-int(cal_range/2):i+int(cal_range/2)+1])
                if local_max == col_data[i + index_min]:
                    # print('Max! : ' + str(i))
                    x.append(i + index_min)
                    # y.append(col_data[i + index_min])
            return [x[i+1] - x[i] for i in range(0, len(x)-1)]
            # return list(range(1, len(x))), [x[i+1] - x[i] for i in range(0, len(x)-1)]

        if len(strain_compare_info) < 1:
            print("No comparison.")
            return
        else :
            data_types_dict = self.types_dict
            for graph_name, target_list in strain_compare_info.items():
                graph_name = '&'.join([self.subtitle_and_color[target_number][1] for target_number in target_list])
                print('Name : ' + graph_name)
                plot_count : int = 1
                fig = plt.figure(figsize=(col_number*graph_width, -(-len(strain_compare_info)//col_number)*graph_length*2))
                # fig.suptitle('Strains comparison')
                period_dict = {}
                handles = []
                labels = []
                ax =  fig.add_subplot(-(-len(strain_compare_info)//col_number)*2, col_number, plot_count)
                print(f'系統名 : 周期平均')
                for target_number in target_list:
                    periods = []
                    try :
                        for col in data_types_dict[target_number]:
                            line = ax.plot(col.index, col, color=self.subtitle_and_color[target_number][0])
                            # print(f'mean = {mean(peak_detection(col, cal_range))}')
                            periods.append(mean(peak_detection(col, cal_range)))
                        print(f'{self.subtitle_and_color[target_number][1]} : {mean(periods)}')
                        # print(list(periods))
                    except KeyError:
                        print(f"エラー：系統番号 {target_number} は96well_positionsに登録されていません。")
                        return
                    else :
                        handles.append(line[0])
                        labels.append(self.subtitle_and_color[target_number][1])
                    # print(f'periods = {periods}')
                    period_dict[self.subtitle_and_color[target_number][1]] = periods
                ax.legend(handles, labels)
                plot_count = plot_count + 1

                n_rythm = int(-(-((len(data_types_dict[target_number][0])-1)/(60/self.common_setting["sampling_period"]))//24))
                ax.set_title(graph_name)
                ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm+1))
                ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm*4+1), minor=True)
                ax.set_xlabel(self.common_setting["x_axis_title"])
                if self.common_setting["yaxis_share_switch"]:
                    ax.set_ylim(0, self.Y_max)
                ax.set_ylabel(self.common_setting["y_axis_title"])
                ax.grid(axis="both")

                handles = []
                labels = []
                ax =  fig.add_subplot(-(-len(strain_compare_info)//col_number)*2, col_number, plot_count)
                for target_number in target_list:
                    try :
                        target_name = self.subtitle_and_color[target_number][1]
                        mean_ = mean(period_dict[target_name])
                        ax.bar(target_name, mean_, yerr=stdev(period_dict[target_name]), capsize=5, color=self.subtitle_and_color[target_number][0])
                        # print(f'{self.subtitle_and_color[target_number][1]} : {mean(list(itertools.chain.from_iterable(periods)))}')
                        # print(list(periods))
                    except KeyError:
                        print(f"エラー：系統番号 {target_number} は96well_positionsに登録されていません。")
                        return
                plot_count = plot_count + 1

                ax.set_title(graph_name)
                # ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm+1))
                # ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm*4+1), minor=True)
                # ax.set_xlabel(self.common_setting["x_axis_title"])
                ax.set_ylim(bar_range[0], bar_range[1])
                ax.set_ylabel('Period [h]')
                ax.grid(axis="both")

                fig.tight_layout()
                if self.common_setting["plot_save_switch"]: # == 1
                    plt.savefig(self.common_setting["save_path"] + f"compare_plot.jpg")
                else :
                    pass
                plt.show()

                for pair in itertools.combinations(target_list, 2):
                    # print(pair)
                    result = stats.ttest_ind(period_dict[self.subtitle_and_color[pair[0]][1]], period_dict[self.subtitle_and_color[pair[1]][1]], equal_var=False)
                    if result.pvalue < 0.05:
                        print(f'「{self.subtitle_and_color[pair[0]][1]}」と「{self.subtitle_and_color[pair[1]][1]}」 -> 差が「ある」（p={result.pvalue}）')
                    else :
                        # print(str(pair) + ' -> 差が「ない」')
                        pass
                if self.common_setting["plot_save_switch"]: # == 1
                    plt.savefig(self.common_setting["save_path"] + f"strain_compare_{graph_name}.jpg")
                else :
                    pass
                print('\n')


    # 株単位での比較
    def clone_compare(self, clone_compare_info={}, random_color = 0, graph_width = 4, graph_length = 4, col_number = 2):
        if len(clone_compare_info) < 1:
            print("No clone comparison.")
        else :
            def col_posi_linker(col_name, positions):
                if col_name[1] == "0":
                    return positions.at[col_name[0], col_name[2]]
                else :
                    return positions.at[col_name[0], col_name[1:3]]

            fig = plt.figure(figsize=(col_number*graph_width, -(-len(clone_compare_info)//col_number)*graph_length))
            # fig.suptitle('Clones comparison')
            plot_count = 1
            for title, clones_tuple in clone_compare_info.items():
                ax =  fig.add_subplot(-(-len(clone_compare_info)//col_number), col_number, plot_count)
                if random_color :
                    try :
                        for col_name in clones_tuple:
                            subtitle_and_color_ = self.subtitle_and_color[col_posi_linker(col_name, self.positions)]
                            ax.plot(self.plot_data[col_name].index, self.plot_data[col_name], label=col_name+f' ({subtitle_and_color_[1]})')
                    except KeyError:
                        print(f"Error : No such cell -> {col_name}")
                        return 
                else :
                    try :
                        for col_name in clones_tuple:
                            subtitle_and_color_ = self.subtitle_and_color[col_posi_linker(col_name, self.positions)]
                            ax.plot(self.plot_data[col_name].index, self.plot_data[col_name], color=subtitle_and_color_[0], label=col_name+f' ({subtitle_and_color_[1]})')
                    except KeyError:
                        print(f"Error : No such cell -> {col_name}")
                        return 
                ax.legend()
                plot_count = plot_count + 1

                n_rythm = int(-(-((len(self.plot_data)-1)/(60/self.common_setting["sampling_period"]))//24))
                ax.set_title(title)
                ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm+1))
                ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm*4+1), minor=True)
                ax.set_xlabel(self.common_setting["x_axis_title"])
                if self.common_setting["yaxis_share_switch"]:
                    ax.set_ylim(0, self.Y_max)
                ax.set_ylabel(self.common_setting["y_axis_title"])
                ax.grid(axis="both")

            fig.tight_layout()
            if self.common_setting["plot_save_switch"]: # == 1
                plt.savefig(self.common_setting["save_path"] + f"clone_compare_plot.jpg")
            else :
                pass
            plt.show()


    def all(self, graph_width = 2.5, graph_length = 2.5, col_number = 12, blank_off = 1, peak_display = 1, cal_range = 12):
        def col_posi_linker(col_name, positions):
            if col_name[1] == "0":
                return positions.at[col_name[0], col_name[2]]
            else :
                return positions.at[col_name[0], col_name[1:3]]

        def peak_detection(col_data, cal_range):
            index_min = min(col_data.index)
            x = []
            y = []
            # for i in range(int(cal_range/2), len(col_data)-int(cal_range/2), 1):
            for i in range(0 + self.common_setting['peak_detection_after'], len(col_data)-1, 1):
                if i-int(cal_range/2) < 0:
                    local_max = max(col_data[0:i+int(cal_range/2)+1])
                else :
                    local_max = max(col_data[i-int(cal_range/2):i+int(cal_range/2)+1])
                if local_max == col_data[i + index_min]:
                    # print('Max! : ' + str(i))
                    x.append(i + index_min)
                    y.append(col_data[i + index_min])
                    # plt.plot(0.1, 1.2, marker='*')
            return x, y


        fig = plt.figure(figsize=(col_number*graph_width, -(-len(self.plot_data.columns)//col_number)*graph_length))
        # fig.suptitle('All')
        plot_count = 1
        for col in self.plot_data:
            ax =  fig.add_subplot(-(-len(self.plot_data.columns)//col_number), col_number, plot_count)
            if col_posi_linker(col, self.positions):
                ax.plot(self.plot_data.index, self.plot_data[col], color = self.subtitle_and_color[col_posi_linker(col, self.positions)][0])
                if peak_display:
                    x, y = peak_detection(self.plot_data[col], cal_range)
                    ax.scatter(x, y, marker='*')
                    ax.set_title(f'{col} : p={len(x)}')
                else :
                    pass
            else : # col_posi_linker(col, positions) == 0
                if blank_off:
                    ax.plot(self.plot_data.index, [0]*len(self.plot_data.index), color = "black")
                else :
                    ax.plot(self.plot_data.index, self.plot_data[col], color = "black")
                ax.set_title(col)
            plot_count = plot_count + 1

            n_rythm = int(-(-((len(self.plot_data[col])-1)/(60/self.common_setting["sampling_period"]))//24))
            ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm+1))
            ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm*4+1), minor=True)
            ax.set_xlabel(self.common_setting["x_axis_title"])
            if self.common_setting["yaxis_share_switch"]:
                ax.set_ylim(0, self.Y_max)
            ax.set_ylabel(self.common_setting["y_axis_title"])
            ax.grid(axis="both")

        fig.tight_layout()
        if self.common_setting["plot_save_switch"]: # == 1
            plt.savefig(self.common_setting["save_path"] + f"all_plot.jpg")
        else :
            pass
        plt.show()


    def period_cal(self, graph_width = 2.5, graph_length = 2.5, col_number = 12, blank_off = 1, cal_range = 6, y_lim = 36):

        def col_posi_linker(col_name, positions):
            if col_name[1] == "0":
                return positions.at[col_name[0], col_name[2]]
            else :
                return positions.at[col_name[0], col_name[1:3]]

        def peak_detection(col_data, cal_range):
            index_min = min(col_data.index)
            x = []
            y = []
            # for i in range(int(cal_range/2), len(col_data)-int(cal_range/2), 1):
            for i in range(0 + self.common_setting['peak_detection_after'], len(col_data)-1, 1):
                if i-int(cal_range/2) < 0:
                    local_max = max(col_data[0:i+int(cal_range/2)+1])
                else :
                    local_max = max(col_data[i-int(cal_range/2):i+int(cal_range/2)+1])
                if local_max == col_data[i + index_min]:
                    # print('Max! : ' + str(i))
                    x.append(i + index_min)
                    y.append(col_data[i + index_min])
                    # plt.plot(0.1, 1.2, marker='*')
            return list(range(1, len(x))), [x[i+1] - x[i] for i in range(0, len(x)-1)]

        period_dict = {}
        fig = plt.figure(figsize=(col_number*graph_width, -(-len(self.plot_data.columns)//col_number)*graph_length))
        fig.suptitle('All')
        plot_count = 1
        # return self.plot_data
        for col in self.plot_data:
            ax =  fig.add_subplot(-(-len(self.plot_data.columns)//col_number), col_number, plot_count)
            if col_posi_linker(col, self.positions):
                # ax.plot(self.plot_data.index, self.plot_data[col], color = self.subtitle_and_color[col_posi_linker(col, self.positions)][0])
                x, y = peak_detection(self.plot_data[col], cal_range)
                ax.bar(x, y, color=self.subtitle_and_color[col_posi_linker(col, self.positions)][0])
                ax.set_title(f'{col} : avrg={round(sum(y)/len(y), 2)}')
                if self.subtitle_and_color[col_posi_linker(col, self.positions)][1] in period_dict.keys():
                    period_dict[self.subtitle_and_color[col_posi_linker(col, self.positions)][1]].append(round(sum(y)/len(y), 2))
                else :
                    period_dict[self.subtitle_and_color[col_posi_linker(col, self.positions)][1]] = [round(sum(y)/len(y), 2)]
                # 参考：https://qiita.com/yuto_ohno/items/d2676e04f2d94fc30248
                # coef=np.polyfit(x, y, 1)
                # appr = np.poly1d(coef)(x)
                # plt.plot(x, appr,  color = 'black', linestyle=':')
                # y_pred = [coef[0]*i+coef[1] for i in x]
                # r2 = r2_score(y, y_pred)
                # ax.text(max(x)/3.7, max(y)*6/8, 'y={:.2f}x + {:.2f}, \n$R^2$={:.2f}'.format(coef[0], coef[1], r2), fontsize=14)

            else : # col_posi_linker(col, positions) == 0
                if blank_off:
                    ax.plot(self.plot_data.index, [0]*len(self.plot_data.index), color = "black")
                else :
                    ax.plot(self.plot_data.index, self.plot_data[col], color = "black")
                ax.set_title(col)
            plot_count = plot_count + 1

            # n_rythm = int(-(-((len(self.plot_data[col])-1)/(60/self.common_setting["sampling_period"]))//24))
            # ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm+1))
            # ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm*4+1), minor=True)
            # ax.set_xlabel(self.common_setting["x_axis_title"])
            # if self.common_setting["yaxis_share_switch"]:
            ax.set_ylim(15, 30)
            # ax.set_ylabel(self.common_setting["y_axis_title"])
            ax.grid(axis="both")

        fig.tight_layout()
        if self.common_setting["plot_save_switch"]: # == 1
            plt.savefig(self.common_setting["save_path"] + f"all_plot.jpg")
        else :
            pass
        plt.show()
        return period_dict


    def wavelenght_cal(self, d_period = 12, graph_width = 2.5, graph_length = 2.5, col_number = 12, blank_off = 1, cal_range = 12, y_lim = 36):
        def col_posi_linker(col_name, positions):
            if col_name[1] == "0":
                return positions.at[col_name[0], col_name[2]]
            else :
                return positions.at[col_name[0], col_name[1:3]]

        def peak_position(col_data, cal_range, d_period):
            index_min = min(col_data.index)
            peak_time = []
            # for i in range(int(cal_range/2), len(col_data)-int(cal_range/2), 1):
            for i in range(0 + self.common_setting['peak_detection_after'], len(col_data)-1, 1):
                if i-int(cal_range/2) < 0:
                    local_max = max(col_data[0:i+int(cal_range/2)+1])
                else :
                    local_max = max(col_data[i-int(cal_range/2):i+int(cal_range/2)+1])
                if local_max == col_data[i + index_min]:
                    peak_time.append(i + index_min)
            return list(range(1, len(peak_time)+1)), [(k-d_period)%24 for k in peak_time], peak_time

        # return self.plot_data
        fig = plt.figure(figsize=(col_number*graph_width, -(-len(self.plot_data.columns)//col_number)*graph_length))
        fig.suptitle('All')
        plot_count = 1
        for col in self.plot_data:
            ax =  fig.add_subplot(-(-len(self.plot_data.columns)//col_number), col_number, plot_count)
            if col_posi_linker(col, self.positions):
                # ax.plot(self.plot_data.index, self.plot_data[col], color = self.subtitle_and_color[col_posi_linker(col, self.positions)][0])
                x, y, _ = peak_position(self.plot_data[col], cal_range, d_period)
                # print('x = ' + str(x))
                # print('y = ' + str(y))
                ax.bar(x, y, color = self.subtitle_and_color[col_posi_linker(col, self.positions)][0])
                # 参考：https://qiita.com/yuto_ohno/items/d2676e04f2d94fc30248
                coef=np.polyfit(x, y, 1)
                appr = np.poly1d(coef)(x)
                plt.plot(x, appr,  color = 'black', linestyle=':')
                y_pred = [coef[0]*i+coef[1] for i in x]
                r2 = r2_score(y, y_pred)
                ax.text(max(x)/3.7, max(y)*6/8, 'y={:.2f}x + {:.2f}, \n$R^2$={:.2f}'.format(coef[0], coef[1], r2), fontsize=14)
                ax.set_title(f'{col} : p={y}')

            else : # col_posi_linker(col, positions) == 0
                if blank_off:
                    ax.plot(self.plot_data.index, [0]*len(self.plot_data.index), color = "black")
                else :
                    ax.plot(self.plot_data.index, self.plot_data[col], color = "black")
                ax.set_title(col)
            plot_count = plot_count + 1

            # n_rythm = int(-(-((len(self.plot_data[col])-1)/(60/self.common_setting["sampling_period"]))//24))
            # ax.set_title(f'{col} : p={len(y)}')
            # ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm+1))
            # ax.set_xticks(np.linspace(0, int(n_rythm*24), n_rythm*4+1), minor=True)
            # ax.set_xlabel(self.common_setting["x_axis_title"])
            # if self.common_setting["yaxis_share_switch"]:
            ax.set_ylim(0, 25)
            # ax.set_ylabel(self.common_setting["y_axis_title"])
            ax.grid(axis="both")

        fig.tight_layout()
        if self.common_setting["plot_save_switch"]: # == 1
            plt.savefig(self.common_setting["save_path"] + f"all_plot.jpg")
        else :
            pass
        plt.show()
