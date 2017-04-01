import csv
from operator import itemgetter

ID_COLUMN = 'id'


def try_parse(value):
    """ Convert a value to a float or int if possible """
    if value is None:
        return None
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


class CSVRuleSet(dict):
    """ RuleSet created from a csv file """
    def __init__(self, filename):
        data = {}
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_row = {}
                for k, v in row.items():
                    new_row[k] = try_parse(v)
                data[try_parse(row[ID_COLUMN])] = new_row
        super(CSVRuleSet, self).__init__(data)

    def apply_associative_table(self, field_name, filename, self_key_name, foreign_key_name, value_maker=itemgetter('quantity')):
        associations = CSVRuleSet(filename)
        for association in associations.values():
            self_key = association[self_key_name]
            foreign_key = association[foreign_key_name]
            if field_name not in self[self_key]:
                self[self_key][field_name] = {}
            self[self_key][field_name][foreign_key] = value_maker(association)


class DictRuleSet(dict):
    """ RuleSet created from a dictionary object """
    def __init__(self, init_data):
        super(DictRuleSet, self).__init__(init_data)


class Config(object):
    @staticmethod
    def verify_unique_indices(fn):
        """ Simple check that the first column of a csv is unique. """
        with open(fn) as f:
            lines = f.readlines()
            indices = [line.split(',')[0] for line in lines if line.strip()]
        for index in set(indices):
            indices.remove(index)
        assert not indices, "Duplicate indices found in %s: %s" % (fn, ', '.join(indices))

    def __init__(self, debug_mode):
        # sanity check before proceeding
        Config.verify_unique_indices('ruledata/seeds.csv')
        Config.verify_unique_indices('ruledata/recipes.csv')
        Config.verify_unique_indices('ruledata/resources.csv')
        Config.verify_unique_indices('ruledata/seed_yields.csv')
        Config.verify_unique_indices('ruledata/recipe_costs.csv')

        self.seeds = CSVRuleSet('ruledata/seeds.csv')
        self.seeds.apply_associative_table('yield', 'ruledata/seed_yields.csv', 'seed_id', 'resource_id')
        self.resources = CSVRuleSet('ruledata/resources.csv')
        self.recipes = CSVRuleSet('ruledata/recipes.csv')
        self.recipes.apply_associative_table('cost', 'ruledata/recipe_costs.csv', 'recipe_id', 'resource_id')

        for res in self.resources:
            if self.resources[res]['name'] == 'cash':
                self.CASH_RESOURCE = res
        assert getattr(self, 'CASH_RESOURCE') is not None  # until we treat cash the same as everything else, make this check

        self.general = DictRuleSet({
            'plotPrice': 20,
            'plotMultiplier': 3,
            'field_width': 15,
            'field_height': 15,
            'starting_field_width': 2,
            'starting_field_height': 2,
            'max_seed_count': 20,
            'starting_resources': {
                self.CASH_RESOURCE: 10,
            },
            'firstRecipe': 'b',
        })

        if debug_mode:
            for resource_id in self.general['starting_resources']:
                self.general['starting_resources'][resource_id] *= 1000
            for seed_id in self.seeds:
                self.seeds[seed_id]['harvestTimeSeconds'] /= 10
                if self.seeds[seed_id]['harvestTimeSeconds'] < 1:
                    self.seeds[seed_id]['harvestTimeSeconds'] = 1
