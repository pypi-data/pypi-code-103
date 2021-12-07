"""

"""

DIANN_OutputDtype = {
    # File
    'File.Name': 'str',
    'Run': 'str',

    # Protein
    'Protein.Group': 'str',
    'Protein.Ids': 'str',
    'Protein.Names': 'object',
    'PG.Quantity': 'float64',
    'PG.Normalised': 'float64',
    'PG.MaxLFQ': 'float64',
    'Protein.Q.Value': 'float64',
    'PG.Q.Value': 'float64',
    'Global.PG.Q.Value': 'float64',
    'First.Protein.Description': 'object',
    'Lib.PG.Q.Value': 'float64',

    # Gene
    'Genes': 'object',
    'Genes.Quantity': 'float64',
    'Genes.Normalised': 'float64',
    'Genes.MaxLFQ': 'float64',
    'Genes.MaxLFQ.Unique': 'float64',
    'GG.Q.Value': 'float64',

    # Peptide
    'Modified.Sequence': 'str',
    'Stripped.Sequence': 'str',
    'Precursor.Id': 'str',
    'Precursor.Charge': 'int',
    'Proteotypic': 'int64',
    'Precursor.Quantity': 'float64',
    'Precursor.Normalised': 'float64',
    'Precursor.Translated': 'float64',

    # Stats & Scores
    'Q.Value': 'float64',
    'PEP': 'float64',
    'Global.Q.Value': 'float64',
    'Translated.Q.Value': 'float64',
    'Lib.Q.Value': 'float64',
    'Mass.Evidence': 'float64',
    'Evidence': 'float64',
    'CScore': 'float64',
    'Decoy.Evidence': 'float64',
    'Decoy.CScore': 'float64',

    # Spec
    'Ms1.Profile.Corr': 'float64',
    'Spectrum.Similarity': 'float64',
    'Fragment.Quant.Raw': 'object',
    'Fragment.Quant.Corrected': 'object',
    'Fragment.Correlations': 'object',
    'MS2.Scan': 'int64',

    'Ms1.Translated': 'float64',
    'Quantity.Quality': 'float64',
    'Ms1.Area': 'float64',

    # PTM
    'PTM.Informative': 'float64',
    'PTM.Specific': 'float64',
    'PTM.Localising': 'float64',
    'PTM.Q.Value': 'float64',
    'PTM.Site.Confidence': 'float64',
    'Lib.PTM.Site.Confidence': 'float64',

    # RT
    'RT': 'float64',
    'iRT': 'float64',
    'RT.Start': 'float64',
    'RT.Stop': 'float64',
    'Predicted.RT': 'float64',
    'Predicted.iRT': 'float64',

    # IM
    'IM': 'float64',
    'iIM': 'float64',
    'Predicted.IM': 'float64',
    'Predicted.iIM': 'float64',
}

DIANN_TsvLibDtype = {
    'FileName': 'object',
    'PrecursorMz': 'float64',
    'ProductMz': 'float64',
    'Tr_recalibrated': 'float64',
    'IonMobility': 'float64',
    'transition_name': 'object',
    'LibraryIntensity': 'float64',
    'transition_group_id': 'object',
    'decoy': 'int64',
    'PeptideSequence': 'object',
    'Proteotypic': 'int64',
    'QValue': 'float64',
    'PGQValue': 'float64',
    'Ms1ProfileCorr': 'float64',
    'ProteinGroup': 'object',
    'ProteinName': 'object',
    'Genes': 'object',
    'FullUniModPeptideName': 'object',
    'ModifiedPeptide': 'object',
    'PrecursorCharge': 'int64',
    'PeptideGroupLabel': 'object',
    'UniprotID': 'object',
    'NTerm': 'int64',
    'CTerm': 'int64',
    'FragmentType': 'object',
    'FragmentCharge': 'int64',
    'FragmentSeriesNumber': 'int64',
    'FragmentLossType': 'object',
    'ExcludeFromAssay': 'bool',
}
