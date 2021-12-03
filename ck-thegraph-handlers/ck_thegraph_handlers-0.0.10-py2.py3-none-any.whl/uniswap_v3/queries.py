
positions = """
    query ($address: String) {
        positions(where: { owner: $address}) {
            id
            owner
            liquidity
            pool {
                id
                tick
                token0Price
                token1Price
                totalValueLockedETH
            }
            tickLower {
              tickIdx
            }
            tickUpper {
              tickIdx
            }
            depositedToken0
            depositedToken1
            withdrawnToken0
            withdrawnToken1
            collectedFeesToken0
            collectedFeesToken1
            token0 {
                id
                symbol
                name
                feesUSD
                decimals
                derivedETH
            }
            token1 {
                id
                symbol
                name
                feesUSD
                decimals
                derivedETH
            }
        }
    }
    """

position_and_snaps = """
    query ($positionId: String) {
        position(id: $positionId) {
            pool {
                id
            }
            tickLower {
                tickIdx
                feeGrowthOutside0X128
                feeGrowthOutside1X128
            }
            tickUpper {
                tickIdx
                feeGrowthOutside0X128
                feeGrowthOutside1X128
            }
        }
        positionSnapshots(where: { position: $positionId }, orderBy: timestamp, orderDirection: asc) {
            blockNumber
            timestamp
            liquidity
            depositedToken0
            depositedToken1
            withdrawnToken0
            withdrawnToken1
            collectedFeesToken0
            collectedFeesToken1
            feeGrowthInside0LastX128
            feeGrowthInside1LastX128
            transaction {
                id
                gasUsed
                gasPrice
            }
        }
    }
    """
