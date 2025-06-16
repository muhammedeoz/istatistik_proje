import pandas as pd
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import numpy as np
import os

class AccidentStatsApp:
    def __init__(self, master):
        self.master = master
        master.title("Traffic Accident Data Analyzer")
        master.geometry("400x300")

        self.df = None
        self.load_data()

        if self.df is not None:
            self.label = tk.Label(master, text="Analyzing: accidents_small.csv")
            self.label.pack(pady=10)

            self.stats_button = tk.Button(master, text="Show Descriptive Stats", command=self.show_statistics)
            self.stats_button.pack(pady=5)

            self.graph_button = tk.Button(master, text="Show Graphs", command=self.show_graphs)
            self.graph_button.pack(pady=5)

            self.ci_button = tk.Button(master, text="Show Confidence Intervals", command=self.show_confidence_intervals)
            self.ci_button.pack(pady=5)

            self.sample_button = tk.Button(master, text="Estimate Sample Size", command=self.estimate_sample_size)
            self.sample_button.pack(pady=5)

            self.test_button = tk.Button(master, text="Perform Hypothesis Test", command=self.perform_hypothesis_test)
            self.test_button.pack(pady=5)
        else:
            messagebox.showerror("Error", "Failed to load 'accidents_small.csv'. Application will close.")
            master.destroy()

    # Projenin başlangıcında CSV dosyasını okuyup self.df adlı veri çerçevesine yükler.
    def load_data(self):
        file_path = os.path.join(os.getcwd(), "accidents_small.csv")
        if os.path.exists(file_path):
            try:
                self.df = pd.read_csv(file_path)[["Distance(mi)", "Visibility(mi)", "Severity"]]
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV:\n{str(e)}")
                self.df = None
        else:
            self.df = None

    # Bu fonksiyon tanımlayıcı istatistikleri hesaplıyor. Distance değişkeni sağa çarpık olduğu için ortalama ve medyan farklı olabilir.
    # 'Distance (mi)' ve 'Visibility(mi)' sütunları için ortalama, medyan, varyans, standart sapma ve standart hata hesaplanıyor.
    def show_statistics(self):
        stats_df = self.df[["Distance(mi)", "Visibility(mi)"]].agg([
            "mean", "median", "var", "std", "sem"
        ]).transpose()
        stats_df.columns = ["Mean", "Median", "Variance", "Std Deviation", "Std Error"]
        messagebox.showinfo("Descriptive Statistics", stats_df.to_string())

    # Histogram ve boxplotlar verinin dağılımını görmemi sağlıyor. Distance için veriler 0'a yığıldığı için eksen sınırlaması ekledim.
    def show_graphs(self):
        if self.df is None:
            messagebox.showerror("Error", "Data not loaded.")
            return

        for column in ["Distance(mi)", "Visibility(mi)"]:
            plt.figure(figsize=(10, 5))
            sns.histplot(self.df[column], bins=30, kde=True)
            plt.title(f"Histogram of {column}")
            plt.xlabel(column)
            plt.ylabel("Frequency")
            if column == "Distance(mi)":
                plt.xlim(0, 1)  # X eksenini sınırlıyoruz
            plt.show()

            plt.figure(figsize=(10, 5))
            sns.boxplot(x=self.df[column])
            plt.title(f"Boxplot of {column}")
            plt.xlabel(column)
            plt.show()

    # Bu butonla, örneğin Distance ortalamasının 0.033 ile 0.104 arasında olduğunu %95 güvenle söylüyorum.
    def show_confidence_intervals(self):
        def ci(series):
            n = len(series)
            mean = np.mean(series)
            stderr = stats.sem(series)
            h = stderr * stats.t.ppf((1 + 0.95) / 2., n - 1)
            return mean - h, mean + h

        ci_dist = ci(self.df["Distance(mi)"])
        ci_vis = ci(self.df["Visibility(mi)"])

        msg = (
            f"95% Confidence Interval for Distance(mi): {ci_dist}\n"
            f"95% Confidence Interval for Visibility(mi): {ci_vis}"
        )
        messagebox.showinfo("Confidence Intervals", msg)

    # Bu fonksiyon örneklem sayısını hesaplıyor. Distance için az veri yeterli ama Visibility çok dağınık olduğu için çok veri gerekiyor.
    def estimate_sample_size(self):
        def required_sample_size(std, margin_error=0.1, confidence=0.90):
            z = stats.norm.ppf((1 + confidence) / 2)
            return int((z * std / margin_error) ** 2)

        dist_n = required_sample_size(self.df["Distance(mi)"].std())
        vis_n = required_sample_size(self.df["Visibility(mi)"].std())

        msg = (
            f"Sample size needed for Distance (±0.1, 90% CI): {dist_n}\n"
            f"Sample size needed for Visibility (±0.1, 90% CI): {vis_n}"
        )
        messagebox.showinfo("Sample Size Estimation", msg)

    # Hipotez testinde, Distance ortalamasının 0.05’ten anlamlı farkı olmadığını gördüm. Yani rastgele bir sapma olabilir.
    # t testi ile bu hipotezi test ediyorum.
    def perform_hypothesis_test(self):
        t_stat, p_value = stats.ttest_1samp(self.df["Distance(mi)"], popmean=0.05)

        msg = (
            f"Hypothesis Test for Distance(mi):\n"
            f"H0: Mean = 0.05\n"
            f"t-statistic = {t_stat:.4f}, p-value = {p_value:.4f}\n"
        )

        if p_value < 0.05:
            msg += "Result: Reject H0 (significant difference)"
        else:
            msg += "Result: Fail to reject H0 (no significant difference)"

        messagebox.showinfo("Hypothesis Test", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = AccidentStatsApp(root)
    root.mainloop()
