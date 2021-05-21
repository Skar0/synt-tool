import dd.cudd as bdd_func


def attractor(arena, s, player, manager):
    """
    Computes the attractor of set s for player in the arena.
    :param arena: the arena in which we compute the attractor
    :type arena: Arena
    :param s: the set for which we compute the attractor
    :type s: dd.cudd.Function
    :param player: the player for which we compute the attractor
    :type player: int
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the computed attractor
    :rtype: dd.cudd.Function
    """

    old_attractor = manager.false
    new_attractor = s  # at first, the attractor only contains s

    # while a fixpoint is not reached
    while old_attractor != new_attractor:

        old_attractor = new_attractor

        # BDD representing the old attractor set, using prime variables
        old_attractor_prime = manager.let(arena.mapping_bis, old_attractor)

        # BDD representing vertices with at least one successor in the old attractor
        bdd_vertices_one_succ = arena.edges & old_attractor_prime
        vertices_one_succ = manager.exist(arena.vars_bis, bdd_vertices_one_succ)

        # BDD representing vertices with at least one successor outside the previous attractor
        # TODO are the vertices in the negation that don't exist ignored since they dont belong to arena.edges ?
        bdd_vertices_all_succ = arena.edges & ~old_attractor_prime

        # vertices for which there does not exist a successor outside the previous attractor
        vertices_all_succ = ~manager.exist(arena.vars_bis, bdd_vertices_all_succ)

        # if we compute the attractor for player 0
        if not player:
            player0_vertices_attractor = arena.player0_vertices & vertices_one_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_all_succ
        else:
            player0_vertices_attractor = arena.player0_vertices & vertices_all_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_one_succ

        new_attractor = old_attractor | player0_vertices_attractor | player1_vertices_attractor

    return new_attractor


def attractor_cudd(arena, s, player, manager):
    """
    Computes the attractor of set s for player in the arena. This version uses cudd-specific functions.
    :param arena: the arena in which we compute the attractor
    :type arena: Arena
    :param s: the set for which we compute the attractor
    :type s: dd.cudd.Function
    :param player: the player for which we compute the attractor
    :type player: int
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the computed attractor
    :rtype: dd.cudd.Function
    """

    old_attractor = manager.false
    new_attractor = s  # at first attractor only contains s

    # while a fixpoint is not reached
    while old_attractor != new_attractor:

        old_attractor = new_attractor

        # BDD representing the old attractor set, using prime variables
        old_attractor_prime = manager.let(arena.mapping_bis, old_attractor)

        # BDD representing vertices with at least one successor in the old attractor
        vertices_one_succ = bdd_func.and_exists(arena.edges, old_attractor_prime, arena.vars_bis)

        # BDD representing vertices with at least one successor outside the previous attractor
        # TODO are the vertices in the negation that don't exist ignored since they dont belong to arena.edges ?
        # TODO is complementing the replaced attractor with prime vars same as replacing variables in complement of att?
        vertices_all_succ = ~bdd_func.and_exists(arena.edges, ~old_attractor_prime, arena.vars_bis)

        # if we compute the attractor for player 0
        if not player:
            player0_vertices_attractor = arena.player0_vertices & vertices_one_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_all_succ
        else:
            player0_vertices_attractor = arena.player0_vertices & vertices_all_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_one_succ

        new_attractor = old_attractor | player0_vertices_attractor | player1_vertices_attractor

    return new_attractor


def monotone_attractor(arena, s, priority, manager):
    """
    Computes the monotone attractor of the target set, meaning the attractor without visiting bigger priorities than
    the one of the target set.
    :param arena: the arena in which we compute the attractor
    :type arena: Arena
    :param s: the set for which we compute the attractor
    :type s: dd.cudd.Function
    :param priority: the priority of vertices in s
    :type priority: int
    :param manager: the BDD manager
    :type manager: dd.cudd.BDD
    :return: the computed attractor
    :rtype: dd.cudd.Function
    """

    player = priority % 2  # the player for which we compute the attractor

    old_attractor = manager.true
    new_attractor = manager.true  # at first attractor only contains s

    vertices_smaller_priority = manager.false
    for prio, bdd in arena.priorities[0].items():
        if prio <= priority:
            vertices_smaller_priority = vertices_smaller_priority | bdd

    # we don't want to include the old attractor in the first iteration, att normal avec retrait a la fin du target ? je crois qu'on doit considere lit avant OU le target set
    first_iteration = True

    # while a fixpoint is not reached
    while old_attractor != new_attractor:

        old_attractor = new_attractor

        # BDD representing the old attractor set, using prime variables
        old_attractor_prime = manager.let(arena.mapping_bis, old_attractor | s)

        # BDD representing vertices with at least one successor in the old attractor
        vertices_one_succ = bdd_func.and_exists(arena.edges, old_attractor_prime, arena.vars_bis)

        # BDD representing vertices with at least one successor outside the previous attractor
        # TODO are the vertices in the negation that don't exist ignored since they dont belong to arena.edges ?
        # TODO is complementing the replaced attractor with prime vars same as replacing variables in complement of att?
        vertices_all_succ = ~bdd_func.and_exists(arena.edges, ~old_attractor_prime, arena.vars_bis)

        # if we compute the attractor for player 0
        if not player:
            player0_vertices_attractor = arena.player0_vertices & vertices_one_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_all_succ
        else:
            player0_vertices_attractor = arena.player0_vertices & vertices_all_succ
            player1_vertices_attractor = arena.player1_vertices & vertices_one_succ

        new_attractor = (old_attractor | player0_vertices_attractor | player1_vertices_attractor) & vertices_smaller_priority # check if this is where we should impose smaller priorities
        # either that or we create a set with only the edges that are from a vertex with correct priority
    return new_attractor
