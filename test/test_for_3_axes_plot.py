import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 生成示例三维数据
x = np.random.rand(100)
y = np.random.rand(100)
z = np.random.rand(100)

# 创建一个新的图形
fig = plt.figure()

# 添加一个3D子图
ax = fig.add_subplot(111, projection='3d')

# 绘制三维数据点
ax.scatter(x, y, z, c='r', marker='o', s=50)

# 设置坐标轴标签
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

# 显示图形
plt.show()
