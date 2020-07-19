import gzip
import plotly.graph_objects as go
import pathlib
import numpy as np
import matplotlib.pyplot as plt

#config
mean_total_length_for_each_ten_thousand_game_npy='mean_total_length_for_each_ten_thousand_game.npy'
mean_black_length_for_each_ten_thousand_game_npy='mean_black_length_for_each_ten_thousand_game.npy'
mean_white_length_for_each_ten_thousand_game_npy='mean_white_length_for_each_ten_thousand_game.npy'
total_length_for_each_game_npy='total_length_for_each_game.npy'
draw_game_number_npy='draw_game_number.npy'

#load
mean_total_length_for_each_ten_thousand_game=np.load(mean_total_length_for_each_ten_thousand_game_npy)
mean_black_length_for_each_ten_thousand_game=np.load(mean_black_length_for_each_ten_thousand_game_npy)
mean_white_length_for_each_ten_thousand_game=np.load(mean_white_length_for_each_ten_thousand_game_npy)
total_length_for_each_game=np.load(total_length_for_each_game_npy)
draw_game_number=np.load(draw_game_number_npy)

#plot
x = np.linspace(1,len(draw_game_number),len(draw_game_number))
plt.plot(x,np.array(draw_game_number),label="draw_game_number")
plt.legend(loc='upper right')
plt.show()

x = np.linspace(1,len(mean_total_length_for_each_ten_thousand_game),len(mean_total_length_for_each_ten_thousand_game))
plt.plot(x,np.array(mean_total_length_for_each_ten_thousand_game),label="total_mean")
plt.plot(x,np.array(mean_black_length_for_each_ten_thousand_game),label="black_mean")
plt.plot(x,np.array(mean_white_length_for_each_ten_thousand_game),label="white_mean")
plt.legend(loc='upper right')
plt.show()


trace1 = go.Histogram(
    x=total_length_for_each_game[-500000:],
    opacity=0.75,
    name = "last 50w",
    marker=dict(color='rgba(171, 50, 96, 0.6)'))
trace2 = go.Histogram(
    x=total_length_for_each_game[:500000],
    opacity=0.75,
    name = "start_50w",
    marker=dict(color='rgba(12, 50, 196, 0.6)'))
layout = go.Layout(barmode='overlay',
                   title=' compare start 500000 and last 500000',
                   xaxis=dict(title='step'),
                   yaxis=dict(title='Count'))
data = [trace1, trace2]
fig = go.Figure(data,layout=layout)
#fig.add_trace(go.Histogram(x=total_length_for_each_game[-500000:], marker={'color': '#666666'}))
#fig.add_trace(go.Histogram(x=total_length_for_each_game[-1000000:-500000], marker={'color': '#666666'}))
fig.write_html("test.html")

