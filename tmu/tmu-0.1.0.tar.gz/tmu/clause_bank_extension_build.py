from cffi import FFI
ffibuilder = FFI()

ffibuilder.cdef("""
    void cb_calculate_clause_outputs_predict(unsigned int *ta_state, int number_of_clauses, int number_of_features, int number_of_state_bits, int number_of_patches, unsigned int *clause_output, unsigned int *Xi);
    void cb_calculate_clause_outputs_update(unsigned int *ta_state, int number_of_clauses, int number_of_features, int number_of_state_bits, int number_of_patches, unsigned int *clause_output, unsigned int *Xi);
    void cb_type_i_feedback(unsigned int *ta_state, int *clause_weights, unsigned int *feedback_to_ta, unsigned int *output_one_patches, int number_of_clauses, int number_of_features, int number_of_state_bits, int number_of_patches, float update_p, float s, unsigned int weighted_clauses, unsigned int boost_true_positive_feedback, unsigned int *Xi);
    void cb_type_ii_feedback(unsigned int *ta_state, int *clause_weights, unsigned int *output_one_patches, int number_of_clauses, int number_of_features, int number_of_state_bits, int number_of_patches, float update_p, unsigned int weighted_clauses, unsigned int *Xi);
    """)

ffibuilder.set_source("tmu._tm",  # name of the output C extension
"""
    #include "./tmu/ClauseBank.h"
""",
    include_dirs=['.'],
    sources=['./tmu/ClauseBank.c'],   # includes pi.c as additional sources
    libraries=['m'])    # on Unix, link with the math library

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
