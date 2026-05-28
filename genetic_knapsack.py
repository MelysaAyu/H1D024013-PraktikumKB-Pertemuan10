import tkinter as tk
from tkinter import ttk, messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ========== DATA KNAPSACK ==========
items = [
    {"name": "Barang1", "profit": 10, "weight": 5},
    {"name": "Barang2", "profit": 40, "weight": 4},
    {"name": "Barang3", "profit": 30, "weight": 6},
    {"name": "Barang4", "profit": 50, "weight": 3},
    {"name": "Barang5", "profit": 35, "weight": 7},
]
max_capacity = 15
num_items = len(items)

# ========== PARAMETER GA ==========
POPULATION_SIZE = 50
GENERATIONS = 100
CROSSOVER_PROB = 0.8
MUTATION_PROB = 0.05
ELITISM = 2

# ========== FUNGSI UTILITY ==========
def decode_chromosome(chromosome):
    profit = sum(items[i]["profit"] for i, bit in enumerate(chromosome) if bit == 1)
    weight = sum(items[i]["weight"] for i, bit in enumerate(chromosome) if bit == 1)
    return profit, weight

def fitness(chromosome):
    profit, weight = decode_chromosome(chromosome)
    return profit if weight <= max_capacity else 0

def create_random_chromosome():
    return [random.randint(0, 1) for _ in range(num_items)]

# ========== SELEKSI (TS) ==========
def tournament_selection(population, fitnesses, tournament_size=3):
    selected = random.sample(list(zip(population, fitnesses)), tournament_size)
    best = max(selected, key=lambda x: x[1])
    return best[0][:]

# ========== CROSSOVER (ONE POINT) ==========
def one_point_crossover(parent1, parent2):
    point = random.randint(1, num_items - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

# ========== MUTASI (INVERSION) ==========
def inversion_mutation(chromosome):
    start, end = sorted(random.sample(range(num_items), 2))
    chromosome[start:end+1] = reversed(chromosome[start:end+1])
    return chromosome

# ========== ALGORITMA GENETIKA ==========
def run_ga(progress_callback=None):
    population = [create_random_chromosome() for _ in range(POPULATION_SIZE)]
    best_fitness_history = []
    avg_fitness_history = []
    best_solution = None
    best_fitness = 0

    for gen in range(GENERATIONS):
        fitnesses = [fitness(chromo) for chromo in population]
        current_best = max(fitnesses)
        current_avg = sum(fitnesses) / POPULATION_SIZE
        best_fitness_history.append(current_best)
        avg_fitness_history.append(current_avg)

        if current_best > best_fitness:
            best_fitness = current_best
            best_idx = fitnesses.index(current_best)
            best_solution = population[best_idx][:]

        # Elitism
        sorted_pop = [x for _, x in sorted(zip(fitnesses, population), key=lambda pair: pair[0], reverse=True)]
        new_population = [sorted_pop[i][:] for i in range(ELITISM)]

        while len(new_population) < POPULATION_SIZE:
            parent1 = tournament_selection(population, fitnesses)
            parent2 = tournament_selection(population, fitnesses)

            if random.random() < CROSSOVER_PROB:
                child1, child2 = one_point_crossover(parent1, parent2)
            else:
                child1, child2 = parent1[:], parent2[:]

            # Mutasi inversion
            if random.random() < MUTATION_PROB:
                child1 = inversion_mutation(child1)
            if random.random() < MUTATION_PROB:
                child2 = inversion_mutation(child2)

            new_population.append(child1)
            if len(new_population) < POPULATION_SIZE:
                new_population.append(child2)

        population = new_population

        if progress_callback:
            progress_callback(gen+1, GENERATIONS)

    final_fitnesses = [fitness(chromo) for chromo in population]
    final_best_idx = final_fitnesses.index(max(final_fitnesses))
    final_best = population[final_best_idx]
    final_profit, final_weight = decode_chromosome(final_best)

    return {
        "best_solution": final_best,
        "best_profit": final_profit,
        "best_weight": final_weight,
        "best_fitness_history": best_fitness_history,
        "avg_fitness_history": avg_fitness_history
    }

# ========== GUI ==========
class GeneticKnapsackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Algoritma Genetika - Knapsack Problem (NIM: H1D024013)")
        self.root.geometry("800x700")

        # Frame data barang
        frame_data = ttk.LabelFrame(root, text="Data Barang & Kapasitas Gudang", padding=10)
        frame_data.pack(fill="x", padx=10, pady=5)
        data_text = "Barang\tKeuntungan\tUkuran\n" + "\n".join(f"{i['name']}\t{i['profit']}\t\t{i['weight']}" for i in items)
        data_text += f"\n\nKapasitas Maksimal Gudang: {max_capacity}"
        ttk.Label(frame_data, text=data_text, font=("Courier", 10)).pack(anchor="w")

        # Frame metode (otomatis sesuai NIM)
        frame_method = ttk.LabelFrame(root, text="Metode Berdasarkan NIM (H1D024013)", padding=10)
        frame_method.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_method, text="Seleksi: Tournament Selection (TS)", foreground="blue").pack(anchor="w")
        ttk.Label(frame_method, text="Crossover: One Point", foreground="blue").pack(anchor="w")
        ttk.Label(frame_method, text="Mutasi: Inversion", foreground="blue").pack(anchor="w")

        # Tombol jalankan
        self.run_btn = ttk.Button(root, text="Jalankan Algoritma Genetika", command=self.run_ga)
        self.run_btn.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(root, mode='determinate', length=400)
        self.progress.pack(pady=5)

        # Hasil teks
        frame_result = ttk.LabelFrame(root, text="Hasil Terbaik", padding=10)
        frame_result.pack(fill="both", expand=True, padx=10, pady=5)
        self.result_text = tk.Text(frame_result, height=8, wrap=tk.WORD)
        self.result_text.pack(fill="both", expand=True)

        # Grafik
        frame_graph = ttk.LabelFrame(root, text="Grafik Evolusi Fitness", padding=10)
        frame_graph.pack(fill="both", expand=True, padx=10, pady=5)
        self.figure = plt.Figure(figsize=(5,3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame_graph)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_progress(self, gen, total):
        self.progress['value'] = (gen / total) * 100
        self.root.update_idletasks()

    def run_ga(self):
        self.run_btn.config(state="disabled")
        self.progress['value'] = 0
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Menjalankan GA dengan Seleksi TS, Crossover One Point, Mutasi Inversion...\n")
        result = run_ga(progress_callback=self.update_progress)

        selected_items = [items[i]["name"] for i, bit in enumerate(result["best_solution"]) if bit == 1]
        output = f"Solusi terbaik:\n"
        output += f"Barang terpilih: {', '.join(selected_items)}\n"
        output += f"Total Keuntungan: {result['best_profit']}\n"
        output += f"Total Ukuran: {result['best_weight']} / {max_capacity}\n"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, output)

        self.ax.clear()
        self.ax.plot(result["best_fitness_history"], label="Best Fitness", color="green")
        self.ax.plot(result["avg_fitness_history"], label="Avg Fitness", color="orange")
        self.ax.set_xlabel("Generasi")
        self.ax.set_ylabel("Fitness")
        self.ax.set_title("Evolusi Fitness")
        self.ax.legend()
        self.canvas.draw()

        self.run_btn.config(state="normal")
        messagebox.showinfo("Selesai", "Algoritma Genetika selesai!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneticKnapsackApp(root)
    root.mainloop()