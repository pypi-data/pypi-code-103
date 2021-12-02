# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[filter-off] 1'] = {
    'data': {
        'allGitHubUsers': {
            'edges': [
                {
                    'node': {
                        'avatarUrl': 'avatar.com/user1',
                        'login': 'user1',
                        'memberships': {
                            'edges': [
                                {
                                    'node': {
                                        'org': {
                                            'login': 'org1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'org': {
                                            'login': 'org2'
                                        }
                                    }
                                }
                            ]
                        },
                        'name': 'User One'
                    }
                },
                {
                    'node': {
                        'avatarUrl': 'avatar.com/user2',
                        'login': 'user2',
                        'memberships': {
                            'edges': [
                                {
                                    'node': {
                                        'org': {
                                            'login': 'org2'
                                        }
                                    }
                                }
                            ]
                        },
                        'name': 'User Two'
                    }
                },
                {
                    'node': {
                        'avatarUrl': 'avatar.com/user3',
                        'login': 'user3',
                        'memberships': {
                            'edges': [
                            ]
                        },
                        'name': 'User Three'
                    }
                }
            ],
            'totalCount': 3
        }
    }
}

snapshots['test_schema[filter-on] 1'] = {
    'data': {
        'allGitHubUsers': {
            'edges': [
                {
                    'node': {
                        'avatarUrl': 'avatar.com/user1',
                        'login': 'user1',
                        'memberships': {
                            'edges': [
                                {
                                    'node': {
                                        'org': {
                                            'login': 'org1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'org': {
                                            'login': 'org2'
                                        }
                                    }
                                }
                            ]
                        },
                        'name': 'User One'
                    }
                },
                {
                    'node': {
                        'avatarUrl': 'avatar.com/user2',
                        'login': 'user2',
                        'memberships': {
                            'edges': [
                                {
                                    'node': {
                                        'org': {
                                            'login': 'org2'
                                        }
                                    }
                                }
                            ]
                        },
                        'name': 'User Two'
                    }
                }
            ],
            'totalCount': 2
        }
    }
}

snapshots['test_schema[one] 1'] = {
    'data': {
        'allGitHubUsers': {
            'edges': [
                {
                    'node': {
                        'avatarUrl': 'avatar.com/user1',
                        'login': 'user1',
                        'memberships': {
                            'edges': [
                                {
                                    'node': {
                                        'org': {
                                            'login': 'org1'
                                        }
                                    }
                                },
                                {
                                    'node': {
                                        'org': {
                                            'login': 'org2'
                                        }
                                    }
                                }
                            ]
                        },
                        'name': 'User One'
                    }
                },
                {
                    'node': {
                        'avatarUrl': 'avatar.com/user2',
                        'login': 'user2',
                        'memberships': {
                            'edges': [
                                {
                                    'node': {
                                        'org': {
                                            'login': 'org2'
                                        }
                                    }
                                }
                            ]
                        },
                        'name': 'User Two'
                    }
                },
                {
                    'node': {
                        'avatarUrl': 'avatar.com/user3',
                        'login': 'user3',
                        'memberships': {
                            'edges': [
                            ]
                        },
                        'name': 'User Three'
                    }
                }
            ],
            'totalCount': 3
        }
    }
}
