import React, {ChangeEvent, ReactNode, useState} from 'react';
import '../node_modules/react-vis/dist/style.css';
import {LineSeries, VerticalGridLines, HorizontalGridLines, XAxis, YAxis, XYPlot} from 'react-vis';
import {Button, Container} from './App.style';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import {useAsync, useAsyncFn} from 'react-use';
import nanoid from 'nanoid';

const fetchBrandsHook = async (): Promise<string[]> =>
  (await fetch(`/api/brands`)).json();

const fetchModelsHook = async (brand: string): Promise<any> =>
  (await fetch(`/api/models?brand=${brand}`)).json();

function App() {
    const [models, fetchModels] = useAsyncFn(fetchModelsHook);
    const brands = useAsync(fetchBrandsHook)

    const [brand, selectBrand] = useState('')
    const [model, selectModel] = useState('')
    const handleSelectBrand = (event: ChangeEvent<{name?: string, value: unknown}>) => {
        const selectedBrand = event.target?.value as string
        selectBrand(selectedBrand)
        fetchModels(selectedBrand)
    }

    const handleSelectModel = (event: ChangeEvent<{name?: string, value: unknown}>) => {
        selectModel(event.target?.value as string)
    }

    const data = [
        {x: 0, y: 8},
        {x: 1, y: 5},
        {x: 2, y: 4},
        {x: 3, y: 9},
        {x: 4, y: 1},
        {x: 5, y: 7},
        {x: 6, y: 6},
        {x: 7, y: 3},
        {x: 8, y: 2},
        {x: 9, y: 0}
    ];


    return (
        <Container>
            <Select placeholder="Brand" value={brand} onChange={handleSelectBrand}>
                {
                    brands.value ? brands.value.map((brand: string) => <MenuItem value={brand} key={nanoid()}> {brand} </MenuItem>) : null
                }
            </Select>
            <Select placeholder="Model" value={model} onChange={handleSelectModel}>
                {
                    models.value ? models.value.map((model: string) => <MenuItem value={model} key={nanoid()}> {model} </MenuItem>) : null
                }
            </Select>

            <Button onClick={() => console.log("RECHERCHE")}>
                Recherche
            </Button>
            <XYPlot height={300} width={300}>
                <VerticalGridLines/>
                <HorizontalGridLines/>
                <XAxis/>
                <YAxis/>
                <LineSeries data={data}/>
            </XYPlot>
        </Container>
    );
}

export default App;
