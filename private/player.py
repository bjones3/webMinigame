from game_config import get_config
from functools import total_ordering
import time
import heapq
import math
from collections import Counter

_config = get_config()

NUM_PLOTS = _config['field_size'][0] * _config['field_size'][1]
SEEDS = _config['seeds']

profits = {}
for seed, data in SEEDS.items():
    profits[seed] = 24 * 60 * 60 * ((data['harvestYield'] - 1) * data['sellCost']) / data['harvestTimeSeconds']

best_potential_revenue = NUM_PLOTS * max(profits.values())
best_revenue_seed = min([(SEEDS[k]['buyCost'], k) for k, v in profits.items() if v == max(profits.values())])[1]

seeds_by_revenue = SEEDS.keys()
seeds_by_revenue.sort(key=lambda s: profits[s], reverse=True)

init_count = {k: 0 for k in SEEDS}


@total_ordering
class State(object):
    def __init__(self):
        self.actions = ('start', None)
        self.cash = _config['starting_cash']
        self.plots = ()
        self.seed_counts = dict(init_count)
        self.seed_counts_items = None
        self.time_spent = 0
        self.plot_revenue = None
        self.seed_revenue = None
        self.seed_value = 0
        self.unused_seed_value = None
        self.timeless_state = None
        self._finishes_at = None
        self._hash = None

    def init(self):
        if self.seed_revenue is None:
            self.calc_seed_revenue()
        if self.plot_revenue is None:
            self.calc_plot_revenue()
        self.seed_counts_items = sorted(self.seed_counts.items())
        self.timeless_state = (self.cash,
                                self.plots,
                                tuple(self.seed_counts_items))
        self._hash = hash((self.time_spent, self.timeless_state))

    def calc_seed_value(self):
        self.seed_value = sum(SEEDS[s]['sellCost'] * self.seed_counts[s] for s in self.seed_counts)
        return self.seed_value

    def calc_plot_revenue(self):
        self.plot_revenue = sum(profits[s[0]] for s in self.plots)
        return self.plot_revenue

    def calc_seed_revenue(self):
        self.seed_revenue = 0
        needed = NUM_PLOTS - len(self.plots)
        for seed in seeds_by_revenue:
            if not needed:
                break
            have = self.seed_counts[seed]
            if have:
                to_add = min(needed, have)
                needed -= to_add
                self.seed_revenue += profits[seed] * to_add
        return self.seed_revenue

    def calc_seed_revenue2(self):
        self.seed_revenue = 0
        needed = NUM_PLOTS - len(self.plots)
        for seed in seeds_by_revenue:
            if not needed:
                break
            have = self.seed_counts[seed]
            if have:
                to_add = min(needed, have)
                needed -= to_add
                self.seed_revenue += profits[seed] * to_add
        return self.seed_revenue

    def __str__(self):
        return '  '.join((str(self.plot_revenue + self.seed_revenue),
                    ','.join(["%s=%s" % (k, v) for k, v in sorted(self.seed_counts_items) if v > 0]),
                    "plot=" + ''.join([k for k, v in self.plots]),
                    "$" + str(self.cash),
                    "t=" + str(self.time_spent),
#                        "tn=" + str(self.finishes_at()),
                          self.actions[0]

                          )
                   )#+ "\n" + ",".join(self.get_action_list)

    def get_action_list(self):
        action_ll = self.actions
        actions = []
        while action_ll:
            actions.append(action_ll[0])
            action_ll = action_ll[1]
        actions.reverse()
        return actions

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return (self.cash == other.cash and
                self.time_spent == other.time_spent and
                self.plots == other.plots and
                self.seed_counts == other.seed_counts)

    def __lt__(self, other):
        """ 'Less than' is a higher priority, so this may look inverted """

        # a, b = self.finishes_at(), other.finishes_at()
        #
        # if a > b:
        #     return False
        # if a < b:
        #     return True

        spr = self.plot_revenue
        ssr = self.seed_revenue
        opr = other.plot_revenue
        osr = other.seed_revenue

        if False and self.time_spent > 0 and other.time_spent > 0:
            spot = self.cash + 100000 * (spr+ssr) / self.time_spent
            opot = other.cash + 100000 * (opr+osr) / other.time_spent
            if spot < opot:
                return False
            if spot > opot:
                return True


        if spr+ssr < opr+osr:
            return False
        if spr+ssr > opr+osr:
            return True
        if spr+ssr == best_potential_revenue:
            if self.time_spent > other.time_spent:
                return False
            if self.time_spent < other.time_spent:
                return True
        if self.cash < other.cash:
            return False
        if self.cash > other.cash:
            return True
        if self.time_spent > other.time_spent:
            return False
        if self.time_spent < other.time_spent:
            return True
        if spr < opr:
            return False
        if spr > opr:
            return True
        s_seed_value = self.seed_value #or self.calc_seed_value()
        o_seed_value = other.seed_value #or other.calc_seed_value()
        if s_seed_value < o_seed_value:
            return False
        if s_seed_value > o_seed_value:
            return True
        s_total_wait = sum(p[1] for p in self.plots)
        o_total_wait = sum(p[1] for p in other.plots)
        if s_total_wait > o_total_wait:
            return False
        if s_total_wait < o_total_wait:
            return True
        return False

    def copy(self, action):
        cp = State()
        cp.actions = (action, self.actions)
        cp.cash = self.cash
        cp.plots = self.plots
        cp.seed_counts = dict(self.seed_counts)
        cp.time_spent = self.time_spent
        return cp

    def buy(self, seed):
        state = self.copy("buy " + seed)
        state.seed_counts[seed] += 1
        state.cash -= SEEDS[seed]['buyCost']
        state.plot_revenue = self.plot_revenue
        state.seed_value += SEEDS[seed]['sellCost']
        state.init()
        return state

    def sell(self, seed):
        state = self.copy("sell " + seed)
        state.seed_counts[seed] -= 1
        state.cash += SEEDS[seed]['sellCost']
        state.plot_revenue = self.plot_revenue
        state.seed_value -= SEEDS[seed]['sellCost']
        state.init()
        return state

    def sow(self, seed):
        state = self.copy("sow " + seed)
        state.seed_counts[seed] -= 1
        plots = list(state.plots)
        plots.append((seed, self.time_spent + SEEDS[seed]['harvestTimeSeconds']))
        plots.sort(key=lambda p: p[1], reverse=True)
        state.plots = tuple(plots)
        state.init()
        return state

    def harvest_soonest_plot(self):
        seed, harvest_time = self.plots[-1]
        state = self.copy("harvest " + seed)
        state.plots = state.plots[:-1]
        state.time_spent = harvest_time
        state.seed_counts[seed] += SEEDS[seed]['harvestYield']
        state.init()
        return state

    def finishes_at(self):
        """ time_spent when this state can achieve max revenue using simple strategy """
        if self._finishes_at is not None:
            return self._finishes_at

        # super quick estimate
        potential_revenue = (self.plot_revenue or self.calc_plot_revenue()) + (
            self.seed_revenue)
        if potential_revenue == 0:
            self._finishes_at = 999999999999 # 6892647 + 1
            return self._finishes_at

        seeds_needed = min(0, NUM_PLOTS - len(filter(lambda p: p[0] == best_revenue_seed, self.plots)) - self.seed_counts[best_revenue_seed])
        cash_needed = seeds_needed * SEEDS[best_revenue_seed]['buyCost'] - self.cash
        time_needed = 24 * 60 * 60 * cash_needed / potential_revenue
        self._finishes_at = self.time_spent + time_needed
        return self._finishes_at





        this = self

        while True:
            potential_revenue = (this.plot_revenue or this.calc_plot_revenue()) + this.seed_revenue
            if best_potential_revenue == potential_revenue:
                if len(this.plots) < NUM_PLOTS:
                    this = this.sow(best_revenue_seed)
                    continue
                cash = this.cash + this.seed_value
                this._finishes_at = this.time_spent - 24 * 60 * 60 * cash / best_potential_revenue
                return this._finishes_at
            if this.cash >= SEEDS[best_revenue_seed]['buyCost']:
                this = this.buy(best_revenue_seed)
                continue
            if len(this.plots) < NUM_PLOTS and max(this.seed_counts.values()) > 0:
                for seed in seeds_by_revenue:
                    if this.seed_counts[seed]:
                        this = this.sow(seed)
                        break
                continue
            if this.plots:
                # estimate
                this = this.harvest_soonest_plot()
                days_needed = math.ceil((SEEDS[best_revenue_seed]['buyCost'] - this.cash) / potential_revenue)
                skip_day = this.copy('harvest %s days' % days_needed)
                skip_day.time_spent += days_needed * 24 * 60 * 60
                skip_day.cash += days_needed * potential_revenue
                this = skip_day
                continue
                # precise
                this = this.harvest_soonest_plot()
                continue
            print "can't finish"
            this._finishes_at = 6892647 + 1
            return this._finishes_at


def next_states(state):
    # if we have more seeds than plots, sell down (doesn't make sense if you can buy more plots)
    for seed, seed_count in state.seed_counts_items:
        slots = NUM_PLOTS - seed_count
        if slots < 0 or len(filter(lambda p: p[0] == seed, state.plots)) > slots:
            return [state.sell(seed)]

    # if you have harvestable plots, harvest them
    if state.plots:
        if state.plots[-1][1] == state.time_spent:
            return [state.harvest_soonest_plot()]

    # if all your plots are full, the only thing you can do if harvest
    if len(state.plots) == NUM_PLOTS:
        return [state.harvest_soonest_plot()]

    # if you can afford the best seed, buy it
    if state.cash > SEEDS[best_revenue_seed]['buyCost']:
        return [state.buy(best_revenue_seed)]

    # things won't get better once you're at max revenue
    if ((state.plot_revenue or state.calc_plot_revenue()) + state.seed_revenue) == best_potential_revenue:
        return []

    nexts = []

    if len(state.plots) < NUM_PLOTS:
        for seed, seed_count in state.seed_counts_items:
            if seed_count:
                nexts.append(state.sow(seed))

    if state.plots:
        # only harvest if you don't have a seed that grows faster than the delay
        can_harvest = True
        for seed, seed_count in state.seed_counts_items:
            if seed_count > 0 and SEEDS[seed]['harvestTimeSeconds'] <= state.plots[-1][1] - state.time_spent:
                can_harvest = False
        if state.actions[0].startswith('buy'):
            can_harvest = False
        if state.actions[0].startswith('sell'):
            can_harvest = False
        if can_harvest:
            nexts.append(state.harvest_soonest_plot())

    if not state.actions[0].startswith('buy'):
        if not state.actions[0].startswith('sow'):
            for seed, seed_count in state.seed_counts_items:
                if seed_count:
                    if state.actions[0] != 'buy ' + seed:
                        nexts.append(state.sell(seed))


    if not state.actions[0].startswith('buy'):
        if len(state.plots) < NUM_PLOTS:
            for seed, seed_data in SEEDS.items():
                if state.seed_counts[seed] == 0:
                    if seed_data['buyCost'] <= state.cash:
                        if state.actions[0] != 'sell ' + seed:
                            nexts.append(state.buy(seed).sow(seed))

    return nexts


states = []
queued = set()
best = State()
best.init()
#best = best.buy('a').buy('a').buy('a').buy('a')#.sow('a').harvest_soonest_plot().harvest_soonest_plot().sow('a').sow('a').sow('a').sow('a')
heapq.heappush(states, best)
fastest_states = {best.timeless_state: best.time_spent}
potential_revenue = 0
set_hits = 0
best_completion = float('inf')

started = time.time()
i = 0

while True:
    state = heapq.heappop(states)
    if fastest_states[state.timeless_state] < state.time_spent:
        continue
    if state.time_spent >= best_completion:
        continue
    if best != state and best > state:
        best = state
        print best
        potential_revenue = best.seed_revenue + best.plot_revenue
        if potential_revenue == best_potential_revenue:
            print sorted(Counter(best.get_action_list()).items())
            print best.get_action_list()[:20]
            best_completion = min(best_completion, best.time_spent)
    for new_state in next_states(state):
        if new_state.timeless_state not in fastest_states or fastest_states[new_state.timeless_state] > new_state.time_spent:
            fastest_states[new_state.timeless_state] = new_state.time_spent
            heapq.heappush(states, new_state)
        else:
            set_hits += 1
    i += 1
    if i % 10000 == 0:
        print "explored %s at %s states/second (%s waiting)" % (i, i / (time.time() - started), len(states))
        print state
    if potential_revenue >= best_potential_revenue and i > 20000:
        break

    if len(states) > 1000:
        states = states[::2]
        heapq.heapify(states)

print "\n---\n"
print best
print 'sh', set_hits


State.__repr__ = State.__str__
start = State()
start.init()

