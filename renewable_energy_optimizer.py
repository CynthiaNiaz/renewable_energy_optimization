import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os 

file_path = input("Please paste the full file path to the dataset (CSV format): ").strip()
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Dataset not found at {file_path}.")
data = pd.read_csv(file_path)

filtered_data = data[data['Entity'] == 'ASEAN (Ember)']

years = filtered_data['Year'].values  
supply_twh = filtered_data['Electricity from solar and wind - TWh'].values
supply_kwh = supply_twh * 1e6 

energy_demand = np.random.uniform(0.8 * supply_kwh, 1.2 * supply_kwh) 

#Simulation Parameters
storage_capacity = 1000  #kWh
storage_efficiency = 0.9 

def calculate_shortfall(allocation, supply, demand, storage_efficiency):
    available_energy = supply + allocation * storage_efficiency  
    return np.maximum(0, demand - available_energy)  

def stochastic_gradient_descent(supply, demand, storage_capacity, storage_efficiency, iterations=1000, learning_rate=0.1, momentum=0.9):
    allocation = np.zeros(len(demand))
    velocity = np.zeros_like(allocation) 
    for _ in range(iterations):
        idx = np.random.randint(len(demand)) 
        shortfall = max(0, demand[idx] - (supply[idx] + allocation[idx] * storage_efficiency))  
        gradient = -2 * shortfall  
        velocity[idx] = momentum * velocity[idx] - learning_rate * gradient 
        allocation[idx] += velocity[idx] 
        allocation[idx] = np.clip(allocation[idx], 0, storage_capacity)  
    return allocation

#Run Optimization
supply = supply_kwh 
optimized_allocation = stochastic_gradient_descent(supply, energy_demand, storage_capacity, storage_efficiency) 
new_shortfalls = calculate_shortfall(optimized_allocation, supply, energy_demand, storage_efficiency)  


plt.figure(figsize=(12, 6))
plt.plot(years, energy_demand, label="Energy Demand", linestyle='--') 
plt.plot(years, supply, label="Energy Supply")  
plt.plot(years, new_shortfalls, label="Optimized Shortfalls", linestyle='-.')  
plt.legend()
plt.xlabel("Year")
plt.ylabel("Energy (kwh)")
plt.title("Optimized Energy Allocation with Stochastic Gradient Descent")
plt.show()

#Run Monte Carlo Simulation
n_simulations = 1000 #Number of Monte Carlo Simulations
shortfall_distributions = []  
for _ in range(n_simulations):
    simulated_supply = supply + np.random.uniform(-0.1 * supply, 0.1 * supply)  
    simulated_demand = energy_demand + np.random.uniform(-0.2 * energy_demand, 0.2 * energy_demand) 
    optimized_allocation = stochastic_gradient_descent(simulated_supply, simulated_demand, storage_capacity, storage_efficiency) 
    total_shortfall = np.sum(calculate_shortfall(optimized_allocation, simulated_supply, simulated_demand, storage_efficiency)) 
    shortfall_distributions.append(total_shortfall)

mean_shortfall = np.mean(shortfall_distributions) 
confidence_interval = np.percentile(shortfall_distributions, [2.5, 97.5])  
value_at_risk = np.percentile(shortfall_distributions, 5)  

print(f"Mean Daily Shortfall: {mean_shortfall:.2f} kwh")
print(f"95% Confidence Interval for Shortfall: {confidence_interval[0]:.2f} to {confidence_interval[1]:.2f} kwh")
print(f"Value at Risk (5%): {value_at_risk:.2f} kwh")

plt.hist(shortfall_distributions, bins=30, alpha=0.75, edgecolor='k') 
plt.title("Distribution of Total Daily Shortfalls")
plt.xlabel("Daily Shortfall (kwh)")
plt.ylabel("Frequency")
plt.axvline(mean_shortfall, color='r', linestyle='dashed', linewidth=2, label="Mean Shortfall") 
plt.axvline(value_at_risk, color='g', linestyle='dashed', linewidth=2, label=f"VaR (5%): {value_at_risk:.2f} kwh") 
plt.legend()
plt.show()
