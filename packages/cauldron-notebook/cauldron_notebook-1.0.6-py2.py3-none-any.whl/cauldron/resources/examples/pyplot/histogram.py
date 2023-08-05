import numpy as np
import matplotlib.pyplot as plt

import cauldron as cd

# Create data to plot
mu = 100
sigma = 15
x = mu + sigma * np.random.randn(10000)

cd.display.markdown(
   """
   # Plotting with PyPlot

   We created a normally-randomized data set centered at $$ @mu = {{ mu }} $$
   and with a standard deviation of $$ @sigma = {{ sigma }} $$.
   """,
   mu=mu,
   sigma=sigma
)

# Histogram of the data
n, bins, patches = plt.hist(
   x=x,
   bins=50,
   facecolor='green',
   alpha=0.75,
   density=1,
)

plt.xlabel('Smarts')
plt.ylabel('Probability')
plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
plt.axis([40, 160, 0, 0.03])
plt.grid(True)

cd.display.pyplot()
