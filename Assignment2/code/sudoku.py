# Sudoku problems.
# The CSP.ac_3() and CSP.backtrack() methods need to be implemented
import time
from csp import CSP, alldiff


def print_solution(solution):
    """
    Convert the representation of a Sudoku solution, as returned from
    the method CSP.backtracking_search(), into a Sudoku board.
    """
    for row in range(width):
        for col in range(width):
            print(solution[f'X{row+1}{col+1}'], end=" ")
            if col == 2 or col == 5:
                print('|', end=" ")
        print("")
        if row == 2 or row == 5:
            print('------+-------+------')


def format_domains(domains, only_nonsingleton=True):
    items = []
    for k in sorted(domains.keys()):
        vals = sorted(domains[k])
        if only_nonsingleton and len(vals) <= 1:
            continue
        items.append(f"{k}: {{{','.join(str(v) for v in vals)}}}")
    if not items and only_nonsingleton:
        return "(Alle domener er singletons etter AC-3)"
    return "\n".join(items)


# Choose Sudoku problem
grid = open('sudoku_hard.txt').read().split()

width = 9
box_width = 3

domains = {}
for row in range(width):
    for col in range(width):
        if grid[row][col] == '0':
            domains[f'X{row+1}{col+1}'] = set(range(1, 10))
        else:
            domains[f'X{row+1}{col+1}'] = {int(grid[row][col])}

edges = []
for row in range(width):
    edges += alldiff([f'X{row+1}{col+1}' for col in range(width)])
for col in range(width):
    edges += alldiff([f'X{row+1}{col+1}' for row in range(width)])
for box_row in range(box_width):
    for box_col in range(box_width):
        cells = []
        edges += alldiff(
            [
                f'X{row+1}{col+1}' for row in range(box_row * box_width, (box_row + 1) * box_width)
                for col in range(box_col * box_width, (box_col + 1) * box_width)
            ]
        )

csp = CSP(
    variables=[f'X{row+1}{col+1}' for row in range(width) for col in range(width)],
    domains=domains,
    edges=edges,
)

print(csp.ac_3())
print_solution(csp.backtracking_search())



# --- AC-3 ---
t0 = time.perf_counter()
ok = csp.ac_3()
t1 = time.perf_counter()
ac3_time = t1 - t0
print("AC-3 result:", ok)
print(f"AC-3 time: {ac3_time:.6f} s")

print("\nDomains after AC-3. Only the ones with multiple possibilities:")
print(format_domains(csp.domains, only_nonsingleton=True))

# --- Backtracking ---
csp.bt_calls = 0
csp.bt_failures = 0

t2 = time.perf_counter()
solution = csp.backtracking_search()
t3 = time.perf_counter()
bt_time = t3 - t2

print(f"\nBacktracking time: {bt_time:.6f} s")
print("bt_calls:", csp.bt_calls)
print("bt_failures:", csp.bt_failures)

print("\nSolutiom:")
print_solution(solution)

print(f"hard & {csp.bt_calls} & {csp.bt_failures} & {ac3_time:.6f} & {bt_time:.6f} & {ac3_time+bt_time:.6f} \\\\")
