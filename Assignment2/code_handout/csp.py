from typing import Any, Optional
from collections import deque


class CSP:
    def __init__(
        self,
        variables: list[str],
        domains: dict[str, set],
        edges: list[tuple[str, str]],
    ):
        """Constructs a CSP instance with the given variables, domains and edges."""
        self.variables = variables
        self.domains = domains

        # Directional constraint table: (Xi, Xj) -> set of allowed (xi, xj)
        self.binary_constraints: dict[tuple[str, str], set] = {}
        for variable1, variable2 in edges:
            self.binary_constraints[(variable1, variable2)] = set()
            for value1 in self.domains[variable1]:
                for value2 in self.domains[variable2]:
                    if value1 != value2:
                        self.binary_constraints[(variable1, variable2)].add((value1, value2))
                        self.binary_constraints[(variable1, variable2)].add((value2, value1))

        # counters for reporting
        self.bt_calls = 0
        self.bt_failures = 0

    # ---------- AC-3 ----------

    def ac_3(self) -> bool:
        """Enforce arc consistency. Returns False if a domain wipes out, else True."""
        queue = deque(self._all_arcs(include_reverse=True))

        while queue:
            Xi, Xj = queue.popleft()
            if self._revise(Xi, Xj):
                if len(self.domains[Xi]) == 0:
                    return False
                for Xk in self._neighbors_incoming(Xi):
                    if Xk != Xj:
                        queue.append((Xk, Xi))
        return True

    def _revise(self, Xi: str, Xj: str) -> bool:
        revised = False
        Dj = self.domains[Xj]
        allowed = self._allowed_pairs(Xi, Xj)

        for x in list(self.domains[Xi]):
            if not any((x, y) in allowed for y in Dj):
                self.domains[Xi].remove(x)
                revised = True
        return revised

    def _allowed_pairs(self, Xi: str, Xj: str) -> set[tuple]:
        bc = self.binary_constraints
        if (Xi, Xj) in bc:
            return bc[(Xi, Xj)]
        if (Xj, Xi) in bc:
            return {(y, x) for (x, y) in bc[(Xj, Xi)]}
        return {(x, y) for x in self.domains[Xi] for y in self.domains[Xj]}

    def _neighbors_incoming(self, X: str) -> set[str]:
        return {a for (a, b) in self.binary_constraints.keys() if b == X}

    def _all_arcs(self, include_reverse: bool = True) -> list[tuple[str, str]]:
        arcs = set(self.binary_constraints.keys())
        if include_reverse:
            for (a, b) in list(arcs):
                arcs.add((b, a))
        return list(arcs)

    # ---------- Backtracking search ----------

    def backtracking_search(self) -> Optional[dict[str, Any]]:
        """Plain backtracking search. Returns assignment or None."""
        self.bt_calls = 0
        self.bt_failures = 0

        def is_consistent(var: str, val: Any, assignment: dict[str, Any]) -> bool:
            for other, oval in assignment.items():
                if (var, other) in self.binary_constraints:
                    if (val, oval) not in self.binary_constraints[(var, other)]:
                        return False
                elif (other, var) in self.binary_constraints:
                    if (oval, val) not in self.binary_constraints[(other, var)]:
                        return False
            return True

        def select_unassigned(assignment: dict[str, Any]) -> str:
            for v in self.variables:
                if v not in assignment:
                    return v
            raise RuntimeError("No unassigned variable left")

        def backtrack(assignment: dict[str, Any]) -> Optional[dict[str, Any]]:
            self.bt_calls += 1
            if len(assignment) == len(self.variables):
                return assignment

            var = select_unassigned(assignment)
            for val in list(self.domains[var]):
                if is_consistent(var, val, assignment):
                    assignment[var] = val
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                    del assignment[var]

            self.bt_failures += 1
            return None

        return backtrack({})


# ---------- Utility ----------

def alldiff(variables: list[str]) -> list[tuple[str, str]]:
    """Return all edges (a,b) where a and b must differ."""
    return [
        (variables[i], variables[j])
        for i in range(len(variables) - 1)
        for j in range(i + 1, len(variables))
    ]


__all__ = ["CSP", "alldiff"]
