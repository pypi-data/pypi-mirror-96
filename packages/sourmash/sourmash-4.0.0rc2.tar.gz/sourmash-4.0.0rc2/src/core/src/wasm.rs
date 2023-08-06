use wasm_bindgen::prelude::*;

use serde_json;

use crate::cmd::ComputeParameters;
use crate::encodings::HashFunctions;
use crate::signature::{Signature, SigsTrait};
use crate::sketch::minhash::KmerMinHash;

#[wasm_bindgen]
impl KmerMinHash {
    #[wasm_bindgen(constructor)]
    pub fn new_with_scaled(
        num: u32,
        ksize: u32,
        is_protein: bool,
        dayhoff: bool,
        hp: bool,
        seed: u32,
        scaled: u32,
        track_abundance: bool,
    ) -> KmerMinHash {
        // TODO: at most one of (prot, dayhoff, hp) should be true

        let hash_function = if dayhoff {
            HashFunctions::murmur64_dayhoff
        } else if hp {
            HashFunctions::murmur64_hp
        } else if is_protein {
            HashFunctions::murmur64_protein
        } else {
            HashFunctions::murmur64_DNA
        };

        KmerMinHash::new(
            scaled as u64,
            ksize,
            hash_function,
            seed as u64,
            track_abundance,
            num,
        )
    }

    #[wasm_bindgen]
    pub fn add_sequence_js(&mut self, buf: &str) {
        self.add_sequence(buf.as_bytes(), true)
            .expect("Error adding sequence");
    }

    #[wasm_bindgen]
    pub fn to_json(&mut self) -> String {
        serde_json::to_string(self).unwrap()
    }
}

#[wasm_bindgen]
impl ComputeParameters {
    #[wasm_bindgen(constructor)]
    pub fn new_with_params() -> ComputeParameters {
        let params = ComputeParameters::default();
        params
    }
}

#[wasm_bindgen]
impl Signature {
    #[wasm_bindgen(constructor)]
    pub fn new_from_params(params: &ComputeParameters) -> Signature {
        //let params = ComputeParameters::default();

        Signature::from_params(&params)
    }

    #[wasm_bindgen]
    pub fn add_sequence_js(&mut self, buf: &str) {
        self.add_sequence(buf.as_bytes(), true)
            .expect("Error adding sequence");
    }

    #[wasm_bindgen]
    pub fn to_json(&mut self) -> String {
        serde_json::to_string(self).unwrap()
    }
}

#[cfg(test)]
mod test {
    use super::*;
    use wasm_bindgen_test::*;

    #[wasm_bindgen_test]
    fn wasm_test() {
        let mut params = ComputeParameters::new_with_params();
        params.set_ksizes(vec![19, 29, 49]);
        let sig = Signature::new_from_params(&params);
        assert_eq!(sig.size(), 3);
    }
}
