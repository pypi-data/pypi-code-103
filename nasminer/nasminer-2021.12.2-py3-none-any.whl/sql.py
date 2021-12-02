from sqlalchemy import create_engine, MetaData

from nasminer import common

uri = common.config.get('db', 'uri', fallback=None)
testbase = common.config.getboolean('db', 'testbase', fallback=False)
if uri is None:
    print('Running in test mode with in-memory db')
    uri = 'sqlite:///:memory:'
    testbase = True

# db = create_engine(uri, echo=True)
db = create_engine(uri)
meta = MetaData(bind=db)

if testbase:
    from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint
    from sqlalchemy import String, Integer, PickleType, CHAR, DateTime, Date, Time

    filest = Table(
        'files',
        meta,
        Column('id', Integer, primary_key=True),
        Column('folder', String),
        Column('filename', String),
        Column('size', Integer),
        Column('mtime', DateTime),
        Column('filetype', String),
        Column('md5', String),
        UniqueConstraint('folder', 'filename'),
    )
    filest.create(checkfirst=True)

    edft = Table(
        'edf',
        meta,
        Column('id', Integer, primary_key=True),
        Column(
            'fileid',
            Integer,
            ForeignKey('files.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False,
        ),
        Column('dtbegin', DateTime),
        Column('dtend', DateTime),
        Column('channels', PickleType),
        Column('fs', Integer),
        Column('location', String),
    )
    edft.create(checkfirst=True)

    syringet = Table(
        'syringes',
        meta,
        Column('id', Integer, primary_key=True),
        Column(
            'fileid',
            Integer,
            ForeignKey('files.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False,
        ),
        Column('dtbegin', DateTime),
        Column('dtend', DateTime),
        Column('syringes', PickleType),
        Column('location', String),
    )
    syringet.create(checkfirst=True)

    ixtrendt = Table(
        'ixtrend',
        meta,
        Column('id', Integer, primary_key=True),
        Column(
            'fileid',
            Integer,
            ForeignKey('files.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False,
        ),
        Column('dtbegin', DateTime),
        Column('dtend', DateTime),
        Column('signals', PickleType),
        Column('signal_type', String),
        Column('datetime_label', String),
        Column('seperator', CHAR),
        Column('decimal', CHAR),
        Column('patientinfo', String),
    )
    ixtrendt.create(checkfirst=True)

    dicomt = Table(
        'dicom',
        meta,
        Column('id', Integer, primary_key=True),
        Column(
            'fileid',
            Integer,
            ForeignKey('files.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False,
        ),
        Column('dt', String),
        Column('modality', String),
        Column('device', String),
        Column('patient_name', String),
        Column('patient_fname', String),
        Column('patient_id', String),
        Column('patient_birth', Date),
        Column('patient_sex', CHAR),
    )
    dicomt.create(checkfirst=True)

    patientst = Table(
        'patients',
        meta,
        Column('id', Integer, primary_key=True),
        Column('salle', String),
        Column('date', Date),
        Column('debut', Time),
        Column('fin', Time),
        Column('intitule', String),
        Column('nip', Integer),
        Column('nom', String),
        Column('prenom', String),
        Column('datenaissance', Date),
        Column('poids', Integer),
        Column('taille', Integer),
        Column('sexe', CHAR),
        Column('atcd', String),
        Column('commentaires', String),
        UniqueConstraint('nip', 'date'),
    )
    patientst.create(checkfirst=True)
