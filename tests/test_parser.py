import unittest

from prometheus_es_exporter.parser import parse_response
from tests.utils import convert_result


# Sample responses generated by running the provided queries on a Elasticsearch
# server populated with the following data (http command = Httpie utility):
# > http -v POST localhost:9200/foo/bar/1 val:=1 group1=a group2=a
# > http -v POST localhost:9200/foo/bar/2 val:=2 group1=a group2=b
# > http -v POST localhost:9200/foo/bar/3 val:=3 group1=b group2=b
class Test(unittest.TestCase):
    maxDiff = None

    def test_query(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 1
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    # ES7 changed the format of hits.total - this tests parsing the new format
    def test_query_es7(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "skipped": 0,
                "successful": 1,
                "total": 1
            },
            "hits": {
                "hits": [],
                "max_score": None,
                "total": {
                    "relation": "eq",
                    "value": 3
                }
            },
            "timed_out": False,
            "took": 3
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 3
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    # effectively tests other singe-value metrics: max,min,sum,cardinality
    def test_avg(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "val_avg": {
        #             "avg": {"field": "val"}
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "val_avg": {
                    "value": 2.0
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 1,
            'val_avg_value': 2
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    # effecively tests other mult-value metrics: percentile_ranks
    def test_percentiles(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "val_percentiles": {
        #             "percentiles": {"field": "val"}
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "val_percentiles": {
                    "values": {
                        "1.0": 1.02,
                        "25.0": 1.5,
                        "5.0": 1.1,
                        "50.0": 2.0,
                        "75.0": 2.5,
                        "95.0": 2.9,
                        "99.0": 2.98
                    }
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 1,
            'val_percentiles_values_1_0': 1.02,
            'val_percentiles_values_5_0': 1.1,
            'val_percentiles_values_25_0': 1.5,
            'val_percentiles_values_50_0': 2.0,
            'val_percentiles_values_75_0': 2.5,
            'val_percentiles_values_95_0': 2.9,
            'val_percentiles_values_99_0': 2.98
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    def test_stats(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "val_stats": {
        #             "stats": {"field": "val"}
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "val_stats": {
                    "avg": 2.0,
                    "count": 3,
                    "max": 3.0,
                    "min": 1.0,
                    "sum": 6.0
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 1,
            'val_stats_avg': 2.0,
            'val_stats_count': 3,
            'val_stats_max': 3.0,
            'val_stats_min': 1.0,
            'val_stats_sum': 6.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    def test_extended_stats(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "val_extended_stats": {
        #             "extended_stats": {"field": "val"}
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "val_extended_stats": {
                    "avg": 2.0,
                    "count": 3,
                    "max": 3.0,
                    "min": 1.0,
                    "std_deviation": 0.816496580927726,
                    "std_deviation_bounds": {
                        "lower": 0.36700683814454793,
                        "upper": 3.632993161855452
                    },
                    "sum": 6.0,
                    "sum_of_squares": 14.0,
                    "variance": 0.6666666666666666
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 1,
            'val_extended_stats_avg': 2.0,
            'val_extended_stats_count': 3,
            'val_extended_stats_max': 3.0,
            'val_extended_stats_min': 1.0,
            'val_extended_stats_sum': 6.0,
            'val_extended_stats_std_deviation': 0.816496580927726,
            'val_extended_stats_std_deviation_bounds_lower': 0.36700683814454793,
            'val_extended_stats_std_deviation_bounds_upper': 3.632993161855452,
            'val_extended_stats_sum_of_squares': 14.0,
            'val_extended_stats_variance': 0.6666666666666666

        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    # Sample response uses extra document in ES instance:
    # > http -v POST localhost:9200/foo/bar/4 dateval='2019-01-01T00:00:00Z'
    def test_datefield_extended_stats(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "val_extended_stats": {
        #             "extended_stats": {"field": "dateval"}
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "val_extended_stats": {
                    "avg": 1546300800000,
                    "avg_as_string": "2019-01-01T00:00:00.000Z",
                    "count": 1,
                    "max": 1546300800000,
                    "max_as_string": "2019-01-01T00:00:00.000Z",
                    "min": 1546300800000,
                    "min_as_string": "2019-01-01T00:00:00.000Z",
                    "std_deviation": 0,
                    "std_deviation_as_string": "1970-01-01T00:00:00.000Z",
                    "std_deviation_bounds": {
                        "upper": 1546300800000,
                        "lower": 1546300800000
                    },
                    "std_deviation_bounds_as_string": {
                        "upper": "2019-01-01T00:00:00.000Z",
                        "lower": "2019-01-01T00:00:00.000Z"
                    },
                    "sum": 1546300800000,
                    "sum_as_string": "2019-01-01T00:00:00.000Z",
                    "sum_of_squares": 2.39104616408064e+24,
                    "sum_of_squares_as_string": "292278994-08-17T07:12:55.807Z",
                    "variance": 0,
                    "variance_as_string": "1970-01-01T00:00:00.000Z"
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 4
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 4,
            'took_milliseconds': 1,
            'val_extended_stats_avg': 1546300800000,
            'val_extended_stats_count': 1,
            'val_extended_stats_max': 1546300800000,
            'val_extended_stats_min': 1546300800000,
            'val_extended_stats_sum': 1546300800000,
            'val_extended_stats_std_deviation': 0,
            'val_extended_stats_std_deviation_bounds_upper': 1546300800000,
            'val_extended_stats_std_deviation_bounds_lower': 1546300800000,
            'val_extended_stats_sum_of_squares': 2.39104616408064e+24,
            'val_extended_stats_variance': 0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    def test_filter(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "group1_filter": {
        #             "filter": {"term": {"group1": "a"}},
        #             "aggs": {
        #                 "val_sum": {
        #                     "sum": {"field": "val"}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group1_filter": {
                    "doc_count": 2,
                    "val_sum": {
                        "value": 3.0
                    }
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 1,
            'group1_filter_doc_count': 2,
            'group1_filter_val_sum_value': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    def test_filters(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "group_filter": {
        #             "filters": {
        #                 "filters": {
        #                     "group_a": {"term": {"group1": "a"}},
        #                     "group_b": {"term": {"group1": "b"}}
        #                 }
        #             },
        #             "aggs": {
        #                 "val_sum": {
        #                     "sum": {"field": "val"}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group_filter": {
                    "buckets": {
                        "group_a": {
                            "doc_count": 2,
                            "val_sum": {
                                "value": 3.0
                            }
                        },
                        "group_b": {
                            "doc_count": 1,
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    }
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 1,
            'group_filter_doc_count{group_filter="group_a"}': 2,
            'group_filter_doc_count{group_filter="group_b"}': 1,
            'group_filter_val_sum_value{group_filter="group_a"}': 3.0,
            'group_filter_val_sum_value{group_filter="group_b"}': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    def test_filters_anonymous(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "group_filter": {
        #             "filters": {
        #                 "filters": [
        #                     {"term": {"group1": "a"}},
        #                     {"term": {"group1": "b"}}
        #                 ]
        #             },
        #             "aggs": {
        #                 "val_sum": {
        #                     "sum": {"field": "val"}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group_filter": {
                    "buckets": [
                        {
                            "doc_count": 2,
                            "val_sum": {
                                "value": 3.0
                            }
                        },
                        {
                            "doc_count": 1,
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    ]
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 1,
            'group_filter_doc_count{group_filter="filter_0"}': 2,
            'group_filter_doc_count{group_filter="filter_1"}': 1,
            'group_filter_val_sum_value{group_filter="filter_0"}': 3.0,
            'group_filter_val_sum_value{group_filter="filter_1"}': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    def test_terms(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "group1_term": {
        #             "terms": {"field": "group1"},
        #             "aggs": {
        #                 "val_sum": {
        #                     "sum": {"field": "val"}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group1_term": {
                    "buckets": [
                        {
                            "doc_count": 2,
                            "key": "a",
                            "val_sum": {
                                "value": 3.0
                            }
                        },
                        {
                            "doc_count": 1,
                            "key": "b",
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    ],
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 2
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 2,
            'group1_term_doc_count_error_upper_bound': 0,
            'group1_term_sum_other_doc_count': 0,
            'group1_term_doc_count{group1_term="a"}': 2,
            'group1_term_val_sum_value{group1_term="a"}': 3.0,
            'group1_term_doc_count{group1_term="b"}': 1,
            'group1_term_val_sum_value{group1_term="b"}': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    def test_terms_numeric(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "val_terms": {
        #             "terms": {"field": "val"},
        #             "aggs": {
        #                 "val_sum": {
        #                     "sum": {"field": "val"}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "total": 5,
                "successful": 5,
                "failed": 0
            },
            "aggregations": {
                "val_terms": {
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0,
                    "buckets": [
                        {
                            "key": 1,
                            "doc_count": 1,
                            "val_sum": {
                                "value": 1.0
                            }
                        },
                        {
                            "key": 2,
                            "doc_count": 1,
                            "val_sum": {
                                "value": 2.0
                            }
                        },
                        {
                            "key": 3,
                            "doc_count": 1,
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    ]
                }
            },
            "hits": {
                "total": 3,
                "max_score": 0.0,
                "hits": []
            },
            "timed_out": False,
            "took": 4
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 4,
            'val_terms_doc_count_error_upper_bound': 0,
            'val_terms_sum_other_doc_count': 0,
            'val_terms_doc_count{val_terms="1"}': 1,
            'val_terms_val_sum_value{val_terms="1"}': 1.0,
            'val_terms_doc_count{val_terms="2"}': 1,
            'val_terms_val_sum_value{val_terms="2"}': 2.0,
            'val_terms_doc_count{val_terms="3"}': 1,
            'val_terms_val_sum_value{val_terms="3"}': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    def test_nested_terms(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "group1_term": {
        #             "terms": {"field": "group1"},
        #             "aggs": {
        #                 "val_sum": {
        #                     "sum": {"field": "val"}
        #                 },
        #                 "group2_term": {
        #                     "terms": {"field": "group2"},
        #                     "aggs": {
        #                         "val_sum": {
        #                             "sum": {"field": "val"}
        #                         }
        #                     }
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "group1_term": {
                    "buckets": [
                        {
                            "doc_count": 2,
                            "group2_term": {
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "a",
                                        "val_sum": {
                                            "value": 1.0
                                        }
                                    },
                                    {
                                        "doc_count": 1,
                                        "key": "b",
                                        "val_sum": {
                                            "value": 2.0
                                        }
                                    }
                                ],
                                "doc_count_error_upper_bound": 0,
                                "sum_other_doc_count": 0
                            },
                            "key": "a",
                            "val_sum": {
                                "value": 3.0
                            }
                        },
                        {
                            "doc_count": 1,
                            "group2_term": {
                                "buckets": [
                                    {
                                        "doc_count": 1,
                                        "key": "b",
                                        "val_sum": {
                                            "value": 3.0
                                        }
                                    }
                                ],
                                "doc_count_error_upper_bound": 0,
                                "sum_other_doc_count": 0
                            },
                            "key": "b",
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    ],
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 2
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 2,
            'group1_term_doc_count_error_upper_bound': 0,
            'group1_term_sum_other_doc_count': 0,
            'group1_term_doc_count{group1_term="a"}': 2,
            'group1_term_val_sum_value{group1_term="a"}': 3.0,
            'group1_term_group2_term_doc_count_error_upper_bound{group1_term="a"}': 0,
            'group1_term_group2_term_sum_other_doc_count{group1_term="a"}': 0,
            'group1_term_group2_term_doc_count{group1_term="a",group2_term="a"}': 1,
            'group1_term_group2_term_val_sum_value{group1_term="a",group2_term="a"}': 1.0,
            'group1_term_group2_term_doc_count{group1_term="a",group2_term="b"}': 1,
            'group1_term_group2_term_val_sum_value{group1_term="a",group2_term="b"}': 2.0,
            'group1_term_doc_count{group1_term="b"}': 1,
            'group1_term_val_sum_value{group1_term="b"}': 3.0,
            'group1_term_group2_term_doc_count_error_upper_bound{group1_term="b"}': 0,
            'group1_term_group2_term_sum_other_doc_count{group1_term="b"}': 0,
            'group1_term_group2_term_doc_count{group1_term="b",group2_term="b"}': 1,
            'group1_term_group2_term_val_sum_value{group1_term="b",group2_term="b"}': 3.0,
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)

    # Tests handling of disallowed characters in labels and metric names
    # The '-'s in the aggregation name aren't allowed in metric names or
    # label keys, so need to be substituted.
    # The number at the start of the aggregation name isn't allowed at
    # the start of metric names or label keys.
    # A double '_' at the start of the label key (post substitutions)
    # is also not allowed.
    def test_bad_chars(self):
        # Query:
        # {
        #     "size": 0,
        #     "query": {
        #         "match_all": {}
        #     },
        #     "aggs": {
        #         "1-group-filter-1": {
        #             "filters": {
        #                 "filters": {
        #                     "group_a": {"term": {"group1": "a"}},
        #                     "group_b": {"term": {"group1": "b"}}
        #                 }
        #             },
        #             "aggs": {
        #                 "val_sum": {
        #                     "sum": {"field": "val"}
        #                 }
        #             }
        #         }
        #     }
        # }
        response = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "aggregations": {
                "1-group-filter-1": {
                    "buckets": {
                        "group_a": {
                            "doc_count": 2,
                            "val_sum": {
                                "value": 3.0
                            }
                        },
                        "group_b": {
                            "doc_count": 1,
                            "val_sum": {
                                "value": 3.0
                            }
                        }
                    }
                }
            },
            "hits": {
                "hits": [],
                "max_score": 0.0,
                "total": 3
            },
            "timed_out": False,
            "took": 1
        }

        expected = {
            'hits': 3,
            'took_milliseconds': 1,
            '__group_filter_1_doc_count{_group_filter_1="group_a"}': 2,
            '__group_filter_1_doc_count{_group_filter_1="group_b"}': 1,
            '__group_filter_1_val_sum_value{_group_filter_1="group_a"}': 3.0,
            '__group_filter_1_val_sum_value{_group_filter_1="group_b"}': 3.0
        }
        result = convert_result(parse_response(response))
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
