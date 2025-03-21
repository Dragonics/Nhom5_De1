import pygame, sys, random, heapq

# Cấu hình cơ bản
GRID_SIZE = 20                        # Kích thước lưới (số ô theo chiều ngang và dọc)
CELL_SIZE = 30                        # Kích thước mỗi ô (đơn vị pixel)
WINDOW_SIZE = GRID_SIZE * CELL_SIZE    # Kích thước cửa sổ game (nền game vuông)

# Định nghĩa các màu sắc sử dụng trong game
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GRAY  = (100, 100, 100)
YELLOW = (255, 255, 0)

# Các cấu hình cho panel hiển thị thông tin thuật toán A*
PANEL_WIDTH = 300                     # Chiều rộng khu vực hiển thị thông tin A*
SCREEN_WIDTH = WINDOW_SIZE + PANEL_WIDTH  # Chiều rộng tổng của cửa sổ game (game + panel)
SCREEN_HEIGHT = WINDOW_SIZE           # Chiều cao cửa sổ game

# Hàm vẽ chữ lên màn hình (dùng cho tiêu đề, thông báo, điểm số,...)
def draw_text(surface, text, size, x, y, color):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

# Hàm hiển thị màn hình menu chính khi khởi động game
def show_main_menu(screen):
    while True:
        screen.fill(BLACK)   # Làm sạch màn hình với màu đen
        draw_text(screen, "Snake A*", 50, WINDOW_SIZE//2, WINDOW_SIZE//4, GREEN)
        draw_text(screen, "Press SPACE to start", 30, WINDOW_SIZE//2, WINDOW_SIZE//2, WHITE)
        pygame.display.flip()  # Cập nhật giao diện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()   # Thoát game khi người dùng đóng cửa sổ
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return   # Bắt đầu game khi nhấn SPACE

# Hàm hiển thị màn hình Game Over với lựa chọn Restart/Quit
def show_game_over(screen, score):
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Game Over!", 50, WINDOW_SIZE//2, WINDOW_SIZE//4, RED)
        draw_text(screen, f"Score: {score}", 30, WINDOW_SIZE//2, WINDOW_SIZE//2, WHITE)
        draw_text(screen, "Press R to restart or Q to quit", 25, WINDOW_SIZE//2, WINDOW_SIZE*3//4, WHITE)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Khởi động lại game
                elif event.key == pygame.K_q:
                    pygame.quit(); sys.exit()  # Thoát game

# Lớp định nghĩa đối tượng Snake (rắn)
class Snake:
    def __init__(self):
        # Khởi tạo rắn với đầu đặt tại giữa lưới
        self.body = [(GRID_SIZE // 2, GRID_SIZE // 2)]
    def move(self, new_head):
        # Di chuyển rắn: thêm đầu mới và loại bỏ đuôi
        self.body.insert(0, new_head)
        self.body.pop()
    def grow(self, new_head):
        # Khi rắn ăn thức ăn, tăng chiều dài bằng cách thêm đầu mới mà không loại bỏ đuôi
        self.body.insert(0, new_head)

# Lớp định nghĩa đối tượng Food (thức ăn)
class Food:
    def __init__(self, snake_body, obstacles):
        # Tìm vị trí ngẫu nhiên không trùng với thân rắn và chướng ngại vật
        self.position = self.random_position(snake_body, obstacles)
    def random_position(self, snake_body, obstacles):
        while True:
            pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if pos not in snake_body and pos not in obstacles:
                return pos

# Lớp định nghĩa đối tượng Obstacle (chướng ngại vật)
class Obstacle:
    def __init__(self, position, direction):
        self.position = position    # Vị trí của chướng ngại vật
        self.direction = direction  # Hướng di chuyển (dx, dy)
    def move(self):
        # Tính toán vị trí mới dựa trên hướng di chuyển
        x, y = self.position
        dx, dy = self.direction
        new_x, new_y = x + dx, y + dy
        # Kiểm tra va chạm với tường: đảo ngược hướng nếu chạm biên lưới
        if new_x < 0 or new_x >= GRID_SIZE:
            dx = -dx
        if new_y < 0 or new_y >= GRID_SIZE:
            dy = -dy
        self.direction = (dx, dy)
        self.position = (x + dx, y + dy)

# Hàm thuật toán A* tìm đường đi từ điểm start đến goal
def astar(start, goal, snake_body, obstacles):
    # Hàm heuristic sử dụng khoảng cách Manhattan để ước tính khoảng cách còn lại
    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    open_set = []  # Danh sách các nút cần duyệt, được lưu dưới dạng heap (hàng đợi ưu tiên)
    # Đẩy nút xuất phát vào open_set: (f, g, current, path)
    heapq.heappush(open_set, (heuristic(start, goal), 0, start, [start]))
    closed_set = set()  # Tập các nút đã duyệt để tránh lặp lại
    # Các ô không thể đi qua: gồm vị trí của thân rắn và chướng ngại vật
    blocked = set(snake_body) | set(obstacles)
    
    while open_set:
        # Lấy nút có giá trị f thấp nhất
        f, cost, current, path = heapq.heappop(open_set)
        # Nếu nút hiện tại là đích, trả về đường đi từ start đến goal
        if current == goal:
            return path
        # Nếu nút này đã được duyệt thì bỏ qua
        if current in closed_set:
            continue
        closed_set.add(current)
        # Duyệt các ô kề (trên, dưới, trái, phải)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            # Kiểm tra ô kề có nằm trong lưới không
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE:
                # Nếu ô này bị chặn (và không phải ô đích) thì bỏ qua
                if neighbor in blocked and neighbor != goal:
                    continue
                new_cost = cost + 1  # Tăng chi phí đi đến ô kề
                # Đẩy ô kề vào open_set với giá trị f = new_cost + heuristic(neighbor, goal)
                heapq.heappush(open_set, (new_cost + heuristic(neighbor, goal), new_cost, neighbor, path+[neighbor]))
    return None  # Nếu không tìm được đường đi hợp lệ, trả về None

# Hàm vẽ panel hiển thị thông tin và debug của thuật toán A*
def draw_astar_panel(screen, path):
    # Vẽ nền cho panel
    panel_rect = pygame.Rect(WINDOW_SIZE, 0, PANEL_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, BLACK, panel_rect)
    # Vẽ tiêu đề cho panel
    draw_text(screen, "A* Debug", 30, WINDOW_SIZE + PANEL_WIDTH//2, 30, YELLOW)
    if path:
        # Hiển thị độ dài đường đi (số bước)
        draw_text(screen, f"Độ dài: {len(path)}", 25, WINDOW_SIZE + PANEL_WIDTH//2, 70, WHITE)
        # Liệt kê từng bước trong đường đi
        for idx, node in enumerate(path):
            text = f"{idx}: {node}"
            draw_text(screen, text, 20, WINDOW_SIZE + PANEL_WIDTH//2, 100 + idx * 20, WHITE)
    else:
        draw_text(screen, "Không tìm thấy đường", 25, WINDOW_SIZE + PANEL_WIDTH//2, SCREEN_HEIGHT//2, RED)

# Hàm chính cho trò chơi
def game_loop(screen):
    clock = pygame.time.Clock()  # Đối tượng đồng hồ để điều chỉnh tốc độ game
    snake = Snake()              # Khởi tạo rắn
    # Khởi tạo danh sách chướng ngại vật với số lượng tăng lên (ví dụ 10)
    obstacles = [
        Obstacle((random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)),
                 random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]))
        for _ in range(10)
    ]
    # Khởi tạo thức ăn với vị trí không trùng với rắn và chướng ngại vật
    food = Food(snake.body, [obs.position for obs in obstacles])
    # Tìm đường đi từ đầu rắn đến vị trí thức ăn bằng thuật toán A*
    path = astar(snake.body[0], food.position, snake.body, [obs.position for obs in obstacles])
    path_index = 1  # Chỉ số bước tiếp theo trong đường đi
    paused = False  # Biến kiểm soát chế độ tạm dừng

    while True:
        # Xử lý các sự kiện (như đóng cửa sổ, nhấn phím)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused  # Bật/tắt chế độ tạm dừng khi nhấn P

        if paused:
            draw_text(screen, "Paused", 50, WINDOW_SIZE//2, WINDOW_SIZE//2, WHITE)
            pygame.display.flip()
            clock.tick(5)
            continue

        # Cập nhật vị trí chướng ngại vật
        for obs in obstacles:
            obs.move()
        obstacles_positions = [obs.position for obs in obstacles]

        # Kiểm tra và cập nhật lại đường đi nếu cần (ví dụ: đường đi hiện tại không hợp lệ nữa)
        if path is None or path_index >= len(path) or path[path_index] in obstacles_positions:
            path = astar(snake.body[0], food.position, snake.body, obstacles_positions)
            path_index = 1

        # Nếu không tìm được đường đi, kết thúc game (trả về điểm dựa trên độ dài rắn)
        if path is None:
            return len(snake.body) - 1

        # Di chuyển rắn theo bước tiếp theo của đường đi
        new_head = path[path_index]
        path_index += 1

        # Kiểm tra va chạm: nếu rắn chạm vào thân hoặc ra khỏi lưới, kết thúc game
        if new_head in snake.body or not (0 <= new_head[0] < GRID_SIZE and 0 <= new_head[1] < GRID_SIZE):
            return len(snake.body) - 1

        # Nếu rắn ăn được thức ăn, tăng chiều dài và tạo thức ăn mới
        if new_head == food.position:
            snake.grow(new_head)
            food = Food(snake.body, obstacles_positions)
            path = astar(snake.body[0], food.position, snake.body, obstacles_positions)
            path_index = 1
        else:
            # Nếu không ăn thức ăn, rắn chỉ di chuyển mà không tăng chiều dài
            snake.move(new_head)

        # Vẽ lại toàn bộ các thành phần trên màn hình game
        screen.fill(BLACK)
        # Vẽ lưới các ô
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GRAY, rect, 1)
        # Vẽ thân rắn
        for pos in snake.body:
            rect = pygame.Rect(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GREEN, rect)
        # Vẽ thức ăn
        rect = pygame.Rect(food.position[0]*CELL_SIZE, food.position[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, rect)
        # Vẽ chướng ngại vật
        for pos in obstacles_positions:
            rect = pygame.Rect(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLUE, rect)
        # Vẽ đường đi được tính bởi thuật toán A* (với viền màu vàng và số thứ tự trên mỗi ô)
        if path is not None:
            for idx, node in enumerate(path):
                x, y = node[0] * CELL_SIZE, node[1] * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, YELLOW, rect, 2)
                draw_text(screen, str(idx), 15, x + CELL_SIZE//2, y + CELL_SIZE//2, YELLOW)

        # Hiển thị điểm số hiện tại của người chơi
        draw_text(screen, f"Score: {len(snake.body)-1}", 25, WINDOW_SIZE - 70, 20, WHITE)
        # Vẽ panel thông tin của A*
        draw_astar_panel(screen, path)

        pygame.display.flip()  # Cập nhật giao diện
        clock.tick(30)       # Giới hạn tốc độ game (60 FPS)

# Hàm main khởi tạo game và vòng lặp chính
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake A*")

    # Hiển thị menu chính trước khi bắt đầu game
    show_main_menu(screen)

    # Vòng lặp chính của trò chơi, cho phép khởi động lại game sau khi game kết thúc
    while True:
        score = game_loop(screen)
        restart = show_game_over(screen, score)
        if not restart:
            break

if __name__ == "__main__":
    main()
