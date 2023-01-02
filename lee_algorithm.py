class LeeFinder():

    def find_path(self, start, end, grid):

        EMPTY = 1

        grid_W = len(grid[0])
        grid_H = len(grid)

        sx = start['x']
        sy = start['y']
        ex = end['x']
        ey = end['y']

        path = []
        runs = 0
        nodes = 4
        delta = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        grid[sy][sx] = 2
        w = 2

        while True:
            stop_wave = True
            for y in range(grid_H):
                for x in range(grid_W):
                    if grid[y][x] == w:
                        for n in range(nodes):
                            nx = x + delta[n][0]
                            ny = y + delta[n][1]
                            if grid[ny][nx] == EMPTY:
                                stop_wave = False
                                grid[ny][nx] = w + 1
                                runs += 1
            w += 1
            if stop_wave or grid[ey][ex] != EMPTY: break
        if stop_wave: return [], runs
            #ВОЗМОЖНО СТОИТ СДВИНУТЬ ВЛЕВО
        length = grid[ey][ex]
        x = ex
        y = ey
        w = length

        while w > 1:
            path.append((x, y))
            w -= 1

            for n in range(nodes):
                nx = x + delta[n][0]
                ny = y + delta[n][1]
                if grid[ny][nx] == w:
                    x += delta[n][0]
                    y += delta[n][1]
                    break
        path.reverse()
        for i in range(grid_H):
            for j in range(grid_W):
                print('%3d' % grid[i][j], end='')
            print()
        return path, runs