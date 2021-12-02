import os
from dnastack.constants import *


# DATA CONNECT
TEST_DATA_CONNECT_URI = (
    os.getenv("E2E_DATA_CONNECT_URI")
    or "https://collection-service.publisher.dnastack.com/collection/library/search/"
)
TEST_DATA_CONNECT_VARIANTS_TABLE = (
    os.getenv("E2E_DATA_CONNECT_VARIANTS_TABLE") or "covid.cloud.variants"
)
TEST_DATA_CONNECT_FILES_TABLE = (
    os.getenv("E2E_DATA_CONNECT_FILES_TABLE") or "covid.cloud.files"
)

# COLLECTIONS
TEST_COLLECTIONS_URI = (
    os.getenv("E2E_COLLECTIONS_URI") or "https://explorer.dnastack.com/api/collections/"
)
TEST_COLLECTION_NAME = (
    os.getenv("E2E_COLLECTION_NAME") or "sars-cov-2-ncbi-sequence-read-archive"
)
TEST_COLLECTION_QUERY = (
    os.getenv("E2E_COLLECTION_QUERY")
    or "SELECT * from viralai2.ncbi_sra_covid.variants LIMIT 10"
)

# DRS
drs_urls = (
    os.getenv("E2E_DRS_URLS").split(",")
    if os.getenv("E2E_DRS_URLS")
    else [
        "drs://drs.international.covidcloud.ca/072f2fb6-8240-4b1e-b736-7868f559c795",
        "drs://drs.international.covidcloud.ca/2dc29273-ebac-49ec-b452-7d835abfa94b",
        "drs://drs.international.covidcloud.ca/e374d7ff-8944-4a6c-944b-78d40dd96654",
    ]
)
drs_filenames = (
    os.getenv("E2E_DRS_FILENAMES").split(",")
    if os.getenv("E2E_DRS_FILENAMES")
    else ["MW592874.fasta", "SRR13820545.fa", "SRR13820554.fa"]
)

TEST_DRS_URLS = drs_urls
TEST_DRS_FILENAMES = drs_filenames

TEST_DRS = dict(zip(drs_urls, drs_filenames))

TEST_DRS_WITH_ACCESS_URL = (
    os.getenv("E2E_DRS_ACCESS_URL")
    or "drs://drs.international.covidcloud.ca/072f2fb6-8240-4b1e-b736-7868f559c795"
)

TEST_DRS_WITH_ACCESS_ID = (
    os.getenv("E2E_DRS_ACCESS_ID")
    or "drs://explorer.alpha.dnastack.com/70cf03ad-1a9b-48e4-b0db-5ef14bf12c3a"
)

# WES
TEST_WES_URI = os.getenv("E2E_WES_URI") or "https://workspaces-wes.beta.dnastack.com/"

# AUTH
TEST_AUTH_PARAMS = {
    "publisher": {
        "url": "https://wallet.publisher.dnastack.com/",
        "client": {
            "redirect_url": "https://wallet.publisher.dnastack.com/",
            "id": "publisher-cli",
            "secret": "WpEmHtAiB73pCrhbEyci42sBFcfmWBdj",
        },
    },
    "prod": {
        "url": "https://wallet.prod.dnastack.com/",
        "client:": {
            "redirect_url": "https://wallet.prod.dnastack.com/",
            "id": "publisher-cli",
            "secret": "xBmI87BDGdDkiVoJRJm1RgnHGy1MxpN1",
        },
    },
    "wes": {
        "url": os.getenv("E2E_WES_WALLET_URI") or "https://wallet.prod.dnastack.com/",
        "client": {
            "id": os.getenv("E2E_WES_WALLET_CLIENT") or "wes-cli-test-client-id",
            "secret": os.getenv("E2E_WES_WALLET_CLIENT_SECRET")
            or "xBmI87BDGdDkiVoJRJm1RgnHGy1MxpN2",
            "redirect_url": os.getenv("E2E_WES_WALLET_REDIRECT_URI")
            or "https://wallet.prod.dnastack.com/",
        },
    },
}
TEST_AUTH_SCOPES = {
    "publisher": (
        "openid "
        "offline_access "
        "drs-object:write "
        "drs-object:access "
        "dataconnect:info "
        "dataconnect:data "
        "dataconnect:query "
        "wes"
    ),
    "wes": "openid offline_access wes",
}

TEST_WALLET_URI = (
    os.getenv("E2E_WALLET_URI") or TEST_AUTH_PARAMS["publisher"]["wallet-uri"]
)

TEST_WALLET_PERSONAL_ACCESS_TOKEN_DNASTACK = os.getenv(
    "E2E_WALLET_PERSONAL_ACCESS_TOKEN_DNASTACK"
)
TEST_WALLET_PERSONAL_ACCESS_TOKEN_PUBLISHER = os.getenv(
    "E2E_WALLET_PERSONAL_ACCESS_TOKEN_PUBLISHER"
)
TEST_WALLET_EMAIL = os.getenv("E2E_WALLET_EMAIL") or "joseph@dnastack.com"

TEST_WALLET_REFRESH_TOKEN = {
    "publisher": os.getenv("REFRESH_TOKEN_PUBLISHER"),
    "prod": os.getenv("REFRESH_TOKEN_DNASTACK"),
    "wes": os.getenv("REFRESH_TOKEN_WES"),
}


TEST_WDL_FILE_CONTENTS = """version 1.0

task say_greeting {
    input {
        String name
    }

    command <<<
        echo "Hello World, my name is ~{name}!"
    >>>

    output {
        String greetings = read_string(stdout())
    }

    runtime {
        docker: "ubuntu:latest"
    }
}

workflow hello_world {
    input {
        String name
    }
    Array[Int] range = [0,1,2,3,4,5,6]

        call say_greeting as first_greeting {
            input: name = name
        }

    scatter (i in range){
      call say_greeting {
          input: name = name
      }
    }

    output {
        String first = first_greeting.greetings
        Array[String] greetings = say_greeting.greetings
    }

}"""

TEST_WDL_INPUT_PARAM_CONTENTS = """{
  "hello_world.name":"Patrick"
}"""

TEST_WDL_TAG_CONTENTS = """{
  "sampleTag1":"tag1"
}"""

TEST_WDL_ENGINE_PARAM_CONTENTS = """{
  "read_from_cache":"true"
}"""

TEST_WDL_MULTI_MAIN = "./tests/cli/files/main.wdl"
TEST_WDL_MULTI_GREETING = "./tests/cli/files/greeting.wdl"
TEST_WDL_MULTI_FAREWELL = "./tests/cli/files/farewell.wdl"
