import os
plato_dir_root = "/home/jiangxuelei/plato"
def run_pagerank(self, args, params):
    is_directed = "false" if params.get("is_directed") == None else params.get("is_directed")
    eps = 0.0001 if params.get("eps") == None else params.get("eps")
    damping = 0.85 if params.get("damping") == None else params.get("damping")
    iterations = 100 if params.get("iterations") == None else params.get("iterations")
    sh_file_path = "sh " + os.getcwd() + os.sep + "plato_shell" + os.sep + "run_pagerank_local.sh {} {} {} {} {} {} {} {} {} "
    print(sh_file_path)
    return_code = os.system(
        sh_file_path.format(plato_dir_root, args.wnum, args.work_cores, args.input, args.output,
                                                                    is_directed, eps, damping, iterations)
    )